from flask import Flask, request, send_file, jsonify, render_template_string
from werkzeug.utils import secure_filename
import os
import tempfile
from datetime import datetime
from pdfixsdk import GetPdfix, kSaveFull
import multiprocessing as mp

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

            # SAFER: iterate backwards to avoid index issues when removing
            count = parent.GetNumChildren()
            for i in range(count - 1, -1, -1):
                child = parent.GetChild(i)
                if child is None:
                    continue

                # recurse first
                clean(child)

                title = (child.GetTitle() or "").lower()
                if any(f in title for f in filters_lower):
                    # move grandchildren up
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

                    # remove the filtered child
                    parent.RemoveChild(i)

        clean(root)

    if not doc.Save(output_pdf, kSaveFull):
        err = pdfix.GetError()
        doc.Close()
        raise Exception("Save failed: " + err)

    doc.Close()


# ========= WORKER FUNCTION TO RUN IN SEPARATE PROCESS =========
def bookmark_worker(q, input_pdf, output_pdf, filters):
    """
    Runs in a separate process. Calls remove_filtered_bookmarks
    and sends result back via Queue.
    """
    try:
        remove_filtered_bookmarks(input_pdf, output_pdf, filters)
        q.put({"success": True, "error": None})
    except Exception as e:
        q.put({"success": False, "error": str(e)})


# ===================== ROUTES =====================
@app.route('/bookmarks', methods=['POST'])
def filter_bookmarks():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400

        file = request.files['file']
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'File must be a PDF'}), 400

        filters = [".pdf", "outline placeholder"]

        filename = secure_filename(file.filename)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        input_path = os.path.join(app.config['UPLOAD_FOLDER'], f"input_{stamp}_{filename}")

        name, ext = os.path.splitext(filename)
        output_filename = f"{name}_output{ext}"
        print("Processing:", output_filename)
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        # Save uploaded PDF
        file.save(input_path)

        # Run PDF processing in a SEPARATE PROCESS with 100-second timeout
        q = mp.Queue()
        p = mp.Process(target=bookmark_worker, args=(q, input_path, output_path, filters))
        p.start()

        # Wait at most 100 seconds
        p.join(60)

        if p.is_alive():
            # Timed out → kill process and cleanup
            print("PDF processing timed out (>60s), terminating worker.")
            p.terminate()
            p.join()

            # Clean temp files
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)

            return jsonify({
                "success": False,
                "error": "PDF processing timed out (over 60 seconds). The PDF may be corrupted."
            }), 504  # 504 Gateway Timeout style

        # Process finished within 100 seconds
        result = q.get() if not q.empty() else {"success": False, "error": "Unknown processing error"}

        # Remove temp input
        if os.path.exists(input_path):
            os.remove(input_path)

        if not result["success"]:
            # Delete bad output file if exists
            if os.path.exists(output_path):
                os.remove(output_path)
            print("Worker error:", result["error"])
            return jsonify({"success": False, "error": result["error"]}), 500

        # If we reach here, output PDF is ready
        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


# ===================== START SERVER =====================
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    # Important for multiprocessing on Windows
    mp.freeze_support()
    app.run(debug=True, host='IS-S3345', port=5059)
