from flask import Flask, request, send_file, jsonify, render_template_string
from werkzeug.utils import secure_filename
import os
import tempfile
from datetime import datetime
from pdfixsdk import GetPdfix, kSaveFull

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()

# Your original function - unchanged
def remove_filtered_bookmarks(input_pdf, output_pdf, filters):
    pdfix = GetPdfix()
    if pdfix is None:
        raise Exception("PDFix initialization failed")
    doc = pdfix.OpenDoc(input_pdf, "")
    if doc is None:
        raise Exception("Failed to open PDF: " + pdfix.GetError())
    root = doc.GetBookmarkRoot()
    if root is None:
        print("No bookmarks found.")
    else:
        filters_lower = [f.lower() for f in filters]
        def clean(parent):
            i = 0
            count = parent.GetNumChildren()
            while i < count:
                child = parent.GetChild(i)
                # Recurse first
                clean(child)
                title = (child.GetTitle() or "").lower()
                match = any(f in title for f in filters_lower)
                if match:
                    # Move child's children into parent at the same position
                    sub_count = child.GetNumChildren()
                    for s in range(sub_count):
                        sub = child.GetChild(s)
                        # Insert this sub-bookmark into parent, before removing pdf bookmark
                        parent.AddChild(i, sub)
                        i += 1
                        count += 1
                    # Now remove .pdf bookmark itself
                    parent.RemoveChild(i)
                    # Do NOT increment i here (because next bookmark is already at same index)
                    count -= 1
                    continue
                i += 1
        clean(root)
    if not doc.Save(output_pdf, kSaveFull):
        err = pdfix.GetError()
        doc.Close()
        raise Exception("Save failed: " + err)
    doc.Close()
    print("Removed only .pdf / Outline placeholder bookmarks and kept structure intact.")
    print("Saved:", output_pdf)

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>PDF Bookmark Filter</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
        }
        .upload-form {
            margin-bottom: 20px;
        }
        input[type="file"] {
            margin: 10px 0;
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        label {
            display: block;
            margin-top: 15px;
            font-weight: bold;
        }
        .help-text {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        button {
            background: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
        }
        button:hover {
            background: #0056b3;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .progress {
            display: none;
            margin-top: 20px;
        }
        .progress-bar {
            width: 100%;
            height: 30px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: #28a745;
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }
        .log {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            max-height: 400px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 12px;
        }
        .log-entry {
            margin: 5px 0;
        }
        .success {
            color: #28a745;
        }
        .error {
            color: #dc3545;
        }
        .download-link {
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            background: #28a745;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }
        .download-link:hover {
            background: #218838;
        }
        .filter-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }
        .filter-tag {
            background: #007bff;
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔖 PDF Bookmark Filter</h1>
        
        <div class="upload-form">
            <form id="uploadForm" enctype="multipart/form-data">
                <div>
                    <label for="file">Select PDF File:</label>
                    <input type="file" id="file" name="file" accept=".pdf" required>
                </div>
                
                <div>
                    <label for="filters">Filter Keywords (comma-separated):</label>
                    <input type="text" id="filters" name="filters" value=".pdf, outline placeholder" 
                           placeholder="e.g., .pdf, outline placeholder, chapter">
                    <div class="help-text">
                        Bookmarks containing these keywords will be removed. Their children will be moved up one level.
                    </div>
                </div>
                
                <button type="submit" id="submitBtn">Filter Bookmarks</button>
            </form>
        </div>

        <div class="progress" id="progress">
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill">0%</div>
            </div>
        </div>

        <div id="result"></div>
        
        <div class="log" id="log" style="display:none;">
            <strong>Processing Log:</strong>
            <div id="logContent"></div>
        </div>
    </div>

    <script>
        const form = document.getElementById('uploadForm');
        const submitBtn = document.getElementById('submitBtn');
        const progress = document.getElementById('progress');
        const progressFill = document.getElementById('progressFill');
        const result = document.getElementById('result');
        const log = document.getElementById('log');
        const logContent = document.getElementById('logContent');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const fileInput = document.getElementById('file');
            const filtersInput = document.getElementById('filters');
            const file = fileInput.files[0];
            const filters = filtersInput.value;
            
            if (!file) {
                alert('Please select a file');
                return;
            }

            const formData = new FormData();
            formData.append('file', file);
            formData.append('filters', filters);

            // Reset UI
            submitBtn.disabled = true;
            submitBtn.textContent = 'Processing...';
            progress.style.display = 'block';
            result.innerHTML = '';
            log.style.display = 'block';
            logContent.innerHTML = '';
            progressFill.style.width = '0%';
            progressFill.textContent = '0%';

            // Better progress simulation
            let currentProgress = 0;
            const interval = setInterval(() => {
                if (currentProgress < 95) {
                    currentProgress += 5;
                    progressFill.style.width = currentProgress + '%';
                    progressFill.textContent = currentProgress + '%';
                }
            }, 200);

            try {
                const response = await fetch('/filter-bookmarks', {
                    method: 'POST',
                    body: formData
                });

                clearInterval(interval);
                
                // Show 100% immediately after response
                progressFill.style.width = '100%';
                progressFill.textContent = '100%';

                const data = await response.json();

                if (data.success) {
                    progressFill.style.width = '100%';
                    progressFill.textContent = '100%';
                    
                    result.innerHTML = `
                        <div class="success">
                            <strong>✅ Filtering Complete!</strong>
                            <p>Filters applied: <strong>${data.filters_applied.join(', ')}</strong></p>
                            <a href="/download/${data.filename}" class="download-link">
                                Download Filtered PDF
                            </a>
                        </div>
                    `;
                    
                    // Display logs
                    if (data.logs && data.logs.length > 0) {
                        data.logs.forEach(log => {
                            const logEntry = document.createElement('div');
                            logEntry.className = 'log-entry';
                            logEntry.textContent = log;
                            logContent.appendChild(logEntry);
                        });
                    }
                } else {
                    result.innerHTML = `
                        <div class="error">
                            <strong>❌ Error:</strong> ${data.error}
                        </div>
                    `;
                }
            } catch (error) {
                clearInterval(interval);
                result.innerHTML = `
                    <div class="error">
                        <strong>❌ Error:</strong> ${error.message}
                    </div>
                `;
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Filter Bookmarks';
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/filter-bookmarks', methods=['POST'])
def filter_bookmarks():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'success': False, 'error': 'File must be a PDF'}), 400
    
    try:
        # Get filters from form
        filters_input = request.form.get('filters', '.pdf, outline placeholder')
        filters = [f.strip() for f in filters_input.split(',') if f.strip()]
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f'input_{timestamp}_{filename}')
        file.save(input_path)
        
        # Create output path
        output_filename = f'filtered_{timestamp}_{filename}'
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        logs = []
        logs.append(f"🔖 Starting bookmark filtering...")
        logs.append(f"📋 Filters: {', '.join(filters)}")
        
        print(f"Processing file: {input_path}")  # Debug log
        print(f"Output will be: {output_path}")  # Debug log
        
        # Call your original function
        remove_filtered_bookmarks(input_path, output_path, filters)
        
        print("Bookmark filtering completed successfully")  # Debug log
        logs.append("✅ Bookmark filtering complete!")
        logs.append(f"🗑️ Removed bookmarks containing: {', '.join(filters)}")
        logs.append("📂 File saved successfully")
        
        # Clean up input file
        os.remove(input_path)
        
        return jsonify({
            'success': True,
            'filename': output_filename,
            'filters_applied': filters,
            'logs': logs
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    print("🚀 Flask PDF Bookmark Filter Server Starting...")
    print("📁 Upload folder:", app.config['UPLOAD_FOLDER'])
    print("🌐 Access the application at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
    app.run(debug=True, host='0.0.0.0', port=5000)
    app.run(debug=True, host='0.0.0.0', port=5000)
    app.run(debug=True, host='0.0.0.0', port=5000)