from flask import Flask, request, send_file, jsonify, render_template_string
from werkzeug.utils import secure_filename
import os
import tempfile
from datetime import datetime
from pdfixsdk import GetPdfix

# Import your transformer classes (make sure transformer.py is in same directory or accessible)
from pdfmodules.transformer_v1 import (
    PdfTagTransformerPhase1,
    Reference,
    Table,
    footprint,
    Table_delete,
    PdfAltTextSetter,
    # Figure_inlineequation,
    # formula_inside_figure_delete,
    # removing_figureTag_inside_P_tag_and_Formula
)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>PDF Tag Changes</title>
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
        button {
            background: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
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
    </style>
</head>
<body>
    <div class="container">
        <h1>📄 PDF Tag changes</h1>
        
        <div class="upload-form">
            <form id="uploadForm" enctype="multipart/form-data">
                <div>
                    <label for="file"><strong>Select PDF File:</strong></label><br>
                    <input type="file" id="file" name="file" accept=".pdf" required>
                </div>
                <button type="submit" id="submitBtn">Transform PDF</button>
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
            const file = fileInput.files[0];
            
            if (!file) {
                alert('Please select a file');
                return;
            }

            const formData = new FormData();
            formData.append('file', file);

            // Reset UI
            submitBtn.disabled = true;
            submitBtn.textContent = 'Processing...';
            progress.style.display = 'block';
            result.innerHTML = '';
            log.style.display = 'block';
            logContent.innerHTML = '';
            progressFill.style.width = '0%';
            progressFill.textContent = '0%';

            // Simulate progress
            let currentProgress = 0;
            const interval = setInterval(() => {
                if (currentProgress < 90) {
                    currentProgress += 10;
                    progressFill.style.width = currentProgress + '%';
                    progressFill.textContent = currentProgress + '%';
                } else {
                    clearInterval(interval);
                }
            }, 1000);

            try {
                const response = await fetch('/transform', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                clearInterval(interval);

                if (data.success) {
                    progressFill.style.width = '100%';
                    progressFill.textContent = '100%';
                    
                    result.innerHTML = `
                        <div class="success">
                            <strong>✅ Transformation Complete!</strong>
                            <a href="/download/${data.filename}" class="download-link">
                                Download Transformed PDF
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
                submitBtn.textContent = 'Transform PDF';
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/transform', methods=['POST'])
def transform_pdf():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'success': False, 'error': 'File must be a PDF'}), 400
    
    try:
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f'input_{timestamp}_{filename}')
        file.save(input_path)
        
        # Create temporary files for each phase
        temp_files = [
            os.path.join(app.config['UPLOAD_FOLDER'], f'phase{i}_{timestamp}.pdf')
            for i in range(1, 9)
        ]
        
        # Initialize PDFix
        pdfix = GetPdfix()
        
        logs = []
        
        # Phase 1
        logs.append("🚀 Starting Phase 1: PdfTagTransformerPhase1")
        phase1 = PdfTagTransformerPhase1(pdfix)
        phase1.modify_pdf_tags(input_path, temp_files[0])
        logs.append("✅ Phase 1 complete")
        
        # Phase 2
        logs.append("🚀 Starting Phase 2: Reference")
        phase2 = Reference(pdfix)
        phase2.modify_pdf_tags(temp_files[0], temp_files[1])
        logs.append("✅ Phase 2 complete")
        
        # Phase 3
        logs.append("🚀 Starting Phase 3: Table")
        phase3 = Table(pdfix)
        phase3.modify_pdf_tags(temp_files[1], temp_files[2])
        logs.append("✅ Phase 3 complete")
        
        # Phase 4
        logs.append("🚀 Starting Phase 4: footprint")
        phase4 = footprint(pdfix)
        phase4.modify_pdf_tags(temp_files[2], temp_files[3])
        logs.append("✅ Phase 4 complete")
        
        # Phase 5
        logs.append("🚀 Starting Phase 5: Table_delete")
        phase5 = Table_delete(pdfix)
        phase5.modify_pdf_tags(temp_files[3], temp_files[4])
        logs.append("✅ Phase 5 complete")
        
        # Phase 6
        logs.append("🚀 Starting Phase 6: PdfAltTextSetter")
        phase6 = PdfAltTextSetter(pdfix)
        output_filename = f'Processed_{filename}'
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        phase6.modify_pdf(temp_files[4],output_path)
        logs.append("✅ Phase 6 complete")
        

        # Phase 7
        # logs.append("🚀 Starting Phase 7: PdfAltTextSetter")
        # phase7 = Figure_inlineequation(pdfix)
        # phase7.modify_pdf_tags(temp_files[5], temp_files[6])
        # logs.append("✅ Phase 6 complete")



        # # Phase 7

        # logs.append("🚀 Starting Phase 7: formula_inside_figure_delete")
        # phase7 = removing_figureTag_inside_P_tag_and_Formula(pdfix)
        # output_filename = f'Processed_{filename}'
        # output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        # phase7.modify_pdf_tags(temp_files[5], output_path)
        # logs.append("✅ Phase 7 complete")
        
        # logs.append("🎉 All transformations complete!")

        # logs.append("🚀 Starting Phase 8: PdfAltTextSetter")
        # phase8 = formula_inside_figure_delete(pdfix)
        # output_filename = f'Processed_{filename}'
        # output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        # phase8.modify_pdf_tags(temp_files[6],output_path)
        # logs.append("✅ Phase 8 complete")




        
        
        # Clean up temporary files
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        os.remove(input_path)
        
        return jsonify({
            'success': True,
            'filename': output_filename,
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
    
    print("🚀 Flask PDF Transformer Server Starting...")
    print("📁 Upload folder:", app.config['UPLOAD_FOLDER'])
    print("🌐 Access the application at: http://localhost:5000")
    app.run(debug=True, host='IS-S3345', port=5051)