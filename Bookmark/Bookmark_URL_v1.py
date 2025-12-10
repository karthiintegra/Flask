from flask import Flask, request, send_file, jsonify, render_template_string
from werkzeug.utils import secure_filename
import os
import tempfile
from datetime import datetime
from pdfixsdk import GetPdfix, kSaveFull
import multiprocessing as mp  # ✅ NEW: for timeout handling

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()


# ===================== BOOKMARK FILTER FUNCTION =====================
def remove_filtered_bookmarks(input_pdf, output_pdf, filters):
    pdfix = GetPdfix()
    if pdfix is None:
        raise Exception("PDFix initialization failed")

    doc = pdfix.OpenDoc(input_pdf, "")
    if doc is None:
        raise Exception("Failed to open PDF: " + pdfix.GetError())

    root = doc.GetBookmarkRoot()
    if root is not None:
        filters_lower = [f.lower() for f in filters]

        def clean(parent):
            if parent is None:
                return

            # ✅ Safer: iterate backwards so we can remove children
            count = parent.GetNumChildren()
            for i in range(count - 1, -1, -1):
                child = parent.GetChild(i)
                if child is None:
                    continue

                # Recurse first
                clean(child)

                title = (child.GetTitle() or "").lower()
                if any(f in title for f in filters_lower):
                    # Move grandchildren up a level
                    gc_count = child.GetNumChildren()
                    grandchildren = []
                    for j in range(gc_count):
                        sub = child.GetChild(j)
                        if sub is not None:
                            grandchildren.append(sub)

                    insert_pos = i + 1
                    for sub in grandchildren:
                        parent.AddChild(insert_pos, sub)
                        insert_pos += 1

                    # Remove the filtered child
                    parent.RemoveChild(i)

        clean(root)

    if not doc.Save(output_pdf, kSaveFull):
        err = pdfix.GetError()
        doc.Close()
        raise Exception("Save failed: " + err)

    doc.Close()


# ===================== WORKER FOR SEPARATE PROCESS =====================
def bookmark_worker(q, input_pdf, output_pdf, filters):
    """
    This runs in a separate process so we can kill it if it hangs.
    """
    try:
        remove_filtered_bookmarks(input_pdf, output_pdf, filters)
        q.put({"success": True, "error": None})
    except Exception as e:
        q.put({"success": False, "error": str(e)})


# ===================== FRONT-END UI (AUTO-DOWNLOAD) =====================
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>PDF Bookmark Filter</title>
    <style>
        body { font-family: Arial; max-width: 700px; margin: 60px auto; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 8px;
                     box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        input[type="file"] { width: 100%; padding: 12px; margin-bottom: 15px;
                             border: 1px solid #ccc; border-radius: 4px; }
        button { width: 100%; padding: 12px; background: #007bff; color: white;
                 border: none; border-radius: 4px; cursor: pointer; font-size: 18px; }
        button:hover { background: #0056b3; }
        .success { color: #28a745; margin-top: 20px; font-size: 18px; }
        .error { color: #b70000; margin-top: 20px; font-size: 18px; }
    </style>
</head>
<body>
<div class="container">
    <h1>🔖 PDF Bookmark Filter</h1>
    <form id="uploadForm" enctype="multipart/form-data">
        <label>Select PDF File:</label>
        <input type="file" name="file" accept=".pdf" required>
        <button type="submit" id="submitBtn">Run</button>
    </form>
    <div id="result"></div>
</div>

<script>
document.getElementById("uploadForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);

    document.getElementById("submitBtn").disabled = true;
    document.getElementById("result").innerHTML = "<p>⏳ Processing PDF...</p>";

    const res = await fetch("/filter-bookmarks", { method: "POST", body: formData });
    const data = await res.json();

    if (data.success) {
        document.getElementById("result").innerHTML =
            "<div class='success'>✔ Completed! Saved in Downloads Folder</div>";

        // 🔥 Auto-start download
        window.location.href = `/download/${data.filename}`;
    } else {
        document.getElementById("result").innerHTML =
            `<div class='error'>❌ ${data.error}</div>`;
    }

    document.getElementById("submitBtn").disabled = false;
});
</script>
</body>
</html>
'''


# ===================== ROUTES =====================
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/filter-bookmarks', methods=['POST'])
def filter_bookmarks():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400

    file = request.files['file']
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'success': False, 'error': 'File must be a PDF'}), 400

    try:
        filters = [".pdf", "outline placeholder"]

        filename = secure_filename(file.filename)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"input_{stamp}_{filename}")

        # Output file name: <name>_output.pdf
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}_output{ext}"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        # Save uploaded file
        file.save(input_path)

        # ✅ Run processing in a separate process with 100s timeout
        q = mp.Queue()
        p = mp.Process(target=bookmark_worker, args=(q, input_path, output_path, filters))
        p.start()

        # Wait at most 100 seconds
        p.join(60)

        if p.is_alive():
            # Timed out → kill worker
            print("⚠ PDF processing timed out (>60s). Terminating worker.")
            p.terminate()
            p.join()

            # Clean up files
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)

            return jsonify({
                'success': False,
                'error': 'PDF processing timed out (over 60 seconds). '
                         'The PDF may be corrupted check your PDF.'
            }), 500

        # Worker finished in time → get result
        result = q.get() if not q.empty() else {"success": False, "error": "Unknown processing error"}

        # Remove temp input
        if os.path.exists(input_path):
            os.remove(input_path)

        if not result["success"]:
            if os.path.exists(output_path):
                os.remove(output_path)
            return jsonify({'success': False, 'error': result["error"]}), 500

        # Success → front-end will then hit /download/<filename>
        return jsonify({'success': True, 'filename': output_filename})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    response = send_file(
        file_path,
        as_attachment=True,
        download_name=filename,
        mimetype="application/pdf"
    )
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


# ===================== START SERVER =====================
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    mp.freeze_support()  # ✅ Important on Windows for multiprocessing
    print("🚀 PDF Bookmark Filter running on: http://localhost:5050")
    app.run(debug=True, host='IS-S3345', port=5050)
