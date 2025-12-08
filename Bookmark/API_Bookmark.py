from flask import Flask, request, send_file, jsonify, render_template_string
from werkzeug.utils import secure_filename
import os
import tempfile
from datetime import datetime
from pdfixsdk import GetPdfix, kSaveFull

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
            i = 0
            count = parent.GetNumChildren()
            while i < count:
                child = parent.GetChild(i)
                clean(child)
                title = (child.GetTitle() or "").lower()
                if any(f in title for f in filters_lower):
                    sub_count = child.GetNumChildren()
                    for s in range(sub_count):
                        sub = child.GetChild(s)
                        parent.AddChild(i, sub)
                        i += 1
                        count += 1
                    parent.RemoveChild(i)
                    count -= 1
                    continue
                i += 1

        clean(root)

    if not doc.Save(output_pdf, kSaveFull):
        err = pdfix.GetError()
        doc.Close()
        print("save Sccess")
        raise Exception("Save failed: " + err)

    doc.Close()




# ===================== ROUTES =====================
# @app.route('/')
# def index():
#     return render_template_string(HTML_TEMPLATE)
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
        print(output_filename)
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)

        # Save uploaded PDF
        file.save(input_path)

        # Process PDF (your function)
        remove_filtered_bookmarks(input_path, output_path, filters)

        # Remove temp input
        os.remove(input_path)

        # Return file to Postman (must use "Send and Download")
        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500


# @app.route('/download/<filename>')
# def download_file(filename):
#     file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

#     response = send_file(
#         file_path,
#         as_attachment=True,
#         download_name=filename,
#         mimetype="application/pdf"
#     )
#     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     response.headers["Pragma"] = "no-cache"
#     response.headers["Expires"] = "0"
#     response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
#     return response


# ===================== START SERVER =====================
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='IS-S3345', port=5059)
