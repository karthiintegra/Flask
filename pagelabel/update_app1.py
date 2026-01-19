# import os
# import glob
# import uuid
# import tempfile
# from bs4 import BeautifulSoup
# from pdfixsdk import GetPdfix, kSaveFull
# from flask import Flask, request, send_file, jsonify

# OUTPUT_FILE = "merged_pginfo.txt"

# # -------------------------------------------------------------------------
# # STEP 1: MERGE PgInfo FILES (Binary Safe)
# # -------------------------------------------------------------------------
# def merge_pginfo_files(folder_path: str):
#     pattern = os.path.join(folder_path, "*.PgInfo")
#     files = glob.glob(pattern)

#     if not files:
#         raise Exception(f"No .PgInfo files found in: {folder_path}")

#     files.sort(key=lambda x: x.lower())
#     output_path = os.path.join(folder_path, OUTPUT_FILE)

#     with open(output_path, "wb") as outfile:
#         for file_path in files:
#             with open(file_path, "rb") as infile:
#                 outfile.write(infile.read())
#                 outfile.write(b"\n")

#     return output_path


# # -------------------------------------------------------------------------
# # STEP 2: PARSE PgInfo AND RETURN VALUES
# # -------------------------------------------------------------------------
# def parse_pginfo(folder_path: str):
#     merged_path = os.path.join(folder_path, OUTPUT_FILE)

#     if not os.path.exists(merged_path):
#         raise Exception(f"Merged PgInfo file not found: {merged_path}")

#     with open(merged_path, "rb") as f:
#         raw = f.read()
#         decoded = raw.decode("latin-1")

#     cleaned = decoded.replace("\x00", "").replace(" ", "")
#     soup = BeautifulSoup(cleaned, "html.parser")

#     filenames = [t.text.strip() for t in soup.find_all("filename")]
#     blankpages = [t.text.strip() for t in soup.find_all("blankpage")]
#     endpages = [t.text.strip() for t in soup.find_all("endpage")]

#     # Find Frontmatter
#     front_idx = None
#     for i, name in enumerate(filenames):
#         if "Frontmatter" in name:
#             front_idx = i
#             break

#     if front_idx is None:
#         raise Exception("Frontmatter not found in PgInfo")

#     # FRONTMATTER BLANK PAGES
#     front_blank_raw = blankpages[front_idx]
#     front_blank_list = []
#     for x in front_blank_raw.split(","):
#         x = x.strip()
#         if x.isdigit():
#             front_blank_list.append(int(x))

#     # OTHER BLANK PAGES
#     other_blank_list = []
#     for idx, entry in enumerate(blankpages):
#         if idx == front_idx:
#             continue
#         for p in entry.split(","):
#             p = p.strip()
#             if p.isdigit():
#                 other_blank_list.append(int(p))

#     # FRONTMATTER ENDPAGE
#     front_end_raw = endpages[front_idx]
#     if not front_end_raw.isdigit():
#         raise Exception(f"Frontmatter endpage is not numeric: {front_end_raw}")
#     front_endpage = int(front_end_raw)

#     return front_blank_list, other_blank_list, front_endpage


# def int_to_roman(num):
#     val = [10, 9, 5, 4, 1]
#     syms = ['x', 'ix', 'v', 'iv', 'i']
#     roman_num = ''
#     i = 0
#     while num > 0 and i < len(val):
#         for _ in range(num // val[i]):
#             roman_num += syms[i]
#             num -= val[i]
#         i += 1
#     return roman_num or ""


# class PageNumberSetter:
#     def __init__(self, pdfix):
#         self.pdfix = pdfix

#     def set_page_labels(
#         self,
#         input_pdf,
#         output_pdf,
#         roman_pages_count=None,
#         roman_skip=None,
#         arabic_skip=None,
#     ):
#         if roman_skip is None:
#             roman_skip = []
#         if arabic_skip is None:
#             arabic_skip = []

#         doc = self.pdfix.OpenDoc(input_pdf, "")
#         if not doc:
#             raise Exception(f"Unable to open PDF: {self.pdfix.GetErrorType()}")

#         try:
#             num_pages = doc.GetNumPages()
#             if num_pages == 0:
#                 raise Exception("PDF has no pages")

#             if roman_pages_count is None:
#                 roman_pages_count = min(24, max(0, num_pages - 1))
#             roman_max_num = max(0, roman_pages_count)

#             root = doc.GetRootObject()
#             if not root:
#                 raise Exception("Unable to get root object")

#             page_labels_dict = root.GetDictionary("PageLabels")
#             if not page_labels_dict:
#                 page_labels_dict = root.PutDict("PageLabels")

#             nums_array = page_labels_dict.GetArray("Nums")
#             if not nums_array:
#                 nums_array = page_labels_dict.PutArray("Nums")

#             while nums_array.GetNumObjects() > 0:
#                 nums_array.RemoveNth(0)

#             # 1) Cover
#             nums_array.PutNumber(nums_array.GetNumObjects(), 0)
#             cover_dict = nums_array.InsertDict(nums_array.GetNumObjects())
#             cover_dict.PutName("Type", "PageLabel")
#             cover_dict.PutString("P", "Cover")

#             # 2) Roman
#             roman_start_idx = 1
#             current_page_idx = roman_start_idx
#             current_roman_num = 1

#             while current_page_idx < num_pages and current_roman_num <= roman_max_num:
#                 while current_roman_num in roman_skip and current_roman_num <= roman_max_num:
#                     current_roman_num += 1
#                 if current_roman_num > roman_max_num:
#                     break

#                 nums_array.PutNumber(nums_array.GetNumObjects(), current_page_idx)
#                 roman_dict = nums_array.InsertDict(nums_array.GetNumObjects())
#                 roman_dict.PutName("Type", "PageLabel")
#                 roman_dict.PutName("S", "r")
#                 roman_dict.PutNumber("St", current_roman_num)

#                 current_page_idx += 1
#                 current_roman_num += 1

#             arabic_start_idx = current_page_idx

#             # 3) Arabic
#             if arabic_start_idx < num_pages:
#                 page_idx = arabic_start_idx
#                 printed_arabic = 1

#                 while page_idx < num_pages:
#                     while printed_arabic in arabic_skip:
#                         printed_arabic += 1

#                     nums_array.PutNumber(nums_array.GetNumObjects(), page_idx)
#                     arabic_dict = nums_array.InsertDict(nums_array.GetNumObjects())
#                     arabic_dict.PutName("Type", "PageLabel")
#                     arabic_dict.PutName("S", "D")
#                     arabic_dict.PutNumber("St", printed_arabic)

#                     page_idx += 1
#                     printed_arabic += 1

#             if not doc.Save(output_pdf, kSaveFull):
#                 raise Exception(f"Unable to save PDF: {self.pdfix.GetErrorType()}")

#         finally:
#             doc.Close()


# def process_pdf_with_pginfo(pdfix, workdir: str, input_pdf: str, output_pdf: str):
#     merge_pginfo_files(workdir)
#     front_blank_list, other_blank_list, front_endpage = parse_pginfo(workdir)

#     setter = PageNumberSetter(pdfix)
#     setter.set_page_labels(
#         input_pdf=input_pdf,
#         output_pdf=output_pdf,
#         roman_pages_count=front_endpage,
#         roman_skip=front_blank_list,
#         arabic_skip=other_blank_list,
#     )


# # ================== FLASK API ==================
# app = Flask(__name__)
# app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB (adjust)

# pdfix = GetPdfix()
# if not pdfix:
#     raise Exception("❌ Pdfix initialization failed")


# @app.route("/health", methods=["GET"])
# def health():
#     return jsonify({"ok": True, "service": "page-labels"})


# @app.route("/api/page-labels", methods=["POST"])
# def api_page_labels():
#     """
#     Multipart form-data:
#       - pdf: single PDF file (required)
#       - pginfo_files: multiple .PgInfo files (required)
#       - output_name: optional output file name
#     Returns:
#       - labeled PDF as attachment
#     """
#     if "pdf" not in request.files:
#         return jsonify({"error": "Missing file field 'pdf'"}), 400

#     pdf_file = request.files["pdf"]
#     pginfo_files = request.files.getlist("pginfo_files")

#     if not pginfo_files or len(pginfo_files) == 0:
#         return jsonify({"error": "Missing file field 'pginfo_files' (upload one or more .PgInfo files)"}), 400

#     # Create isolated temp workdir per request
#     workdir = os.path.join(tempfile.gettempdir(), f"page_labels_{uuid.uuid4().hex}")
#     os.makedirs(workdir, exist_ok=True)

#     try:
#         # Save PDF
#         input_pdf_path = os.path.join(workdir, pdf_file.filename or "input.pdf")
#         pdf_file.save(input_pdf_path)

#         # Save PgInfo files
#         for f in pginfo_files:
#             name = f.filename or f"file_{uuid.uuid4().hex}.PgInfo"
#             # ensure extension
#             if not name.lower().endswith(".pginfo"):
#                 name += ".PgInfo"
#             f.save(os.path.join(workdir, name))

#         # Output name
#         output_name = request.form.get("output_name")
#         if not output_name:
#             base, _ = os.path.splitext(os.path.basename(input_pdf_path))
#             output_name = f"{base}_labeled.pdf"
#         output_pdf_path = os.path.join(workdir, output_name)

#         # Process
#         process_pdf_with_pginfo(pdfix, workdir, input_pdf_path, output_pdf_path)

#         # Return PDF
#         return send_file(
#             output_pdf_path,
#             as_attachment=True,
#             download_name=os.path.basename(output_pdf_path),
#             mimetype="application/pdf",
#         )

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

#     finally:
#         # Optional: cleanup (keep if you want debugging)
#         # Be careful on Windows if file handles are still open.
#         pass


# if __name__ == "__main__":
#     app.run(host="IS-S3345", port=5052, debug=True)



import os
import glob
from bs4 import BeautifulSoup
from pdfixsdk import GetPdfix, kSaveFull
from flask import Flask, request, send_file, jsonify

OUTPUT_FILE = "merged_pginfo.txt"

# -------------------------------------------------------------------------
# STEP 1: MERGE PgInfo FILES (Binary Safe)
# -------------------------------------------------------------------------
def merge_pginfo_files(folder_path: str):
    pattern = os.path.join(folder_path, "*.PgInfo")
    files = glob.glob(pattern)

    if not files:
        raise Exception(f"No .PgInfo files found in: {folder_path}")

    files.sort(key=lambda x: x.lower())
    output_path = os.path.join(folder_path, OUTPUT_FILE)

    with open(output_path, "wb") as outfile:
        for file_path in files:
            with open(file_path, "rb") as infile:
                outfile.write(infile.read())
                outfile.write(b"\n")

    return output_path


# -------------------------------------------------------------------------
# STEP 2: PARSE PgInfo AND RETURN VALUES
# -------------------------------------------------------------------------
def parse_pginfo(folder_path: str):
    merged_path = os.path.join(folder_path, OUTPUT_FILE)

    if not os.path.exists(merged_path):
        raise Exception(f"Merged PgInfo file not found: {merged_path}")

    with open(merged_path, "rb") as f:
        raw = f.read()
        decoded = raw.decode("latin-1")

    cleaned = decoded.replace("\x00", "").replace(" ", "")
    soup = BeautifulSoup(cleaned, "html.parser")

    filenames = [t.text.strip() for t in soup.find_all("filename")]
    blankpages = [t.text.strip() for t in soup.find_all("blankpage")]
    endpages = [t.text.strip() for t in soup.find_all("endpage")]

    # Find Frontmatter
    front_idx = None
    for i, name in enumerate(filenames):
        if "Frontmatter" in name:
            front_idx = i
            break

    if front_idx is None:
        raise Exception("Frontmatter not found in PgInfo")

    # FRONTMATTER BLANK PAGES
    front_blank_raw = blankpages[front_idx]
    front_blank_list = []
    for x in front_blank_raw.split(","):
        x = x.strip()
        if x.isdigit():
            front_blank_list.append(int(x))

    # OTHER BLANK PAGES
    other_blank_list = []
    for idx, entry in enumerate(blankpages):
        if idx == front_idx:
            continue
        for p in entry.split(","):
            p = p.strip()
            if p.isdigit():
                other_blank_list.append(int(p))

    # FRONTMATTER ENDPAGE
    front_end_raw = endpages[front_idx]
    if not front_end_raw.isdigit():
        raise Exception(f"Frontmatter endpage is not numeric: {front_end_raw}")
    front_endpage = int(front_end_raw)

    return front_blank_list, other_blank_list, front_endpage


class PageNumberSetter:
    def __init__(self, pdfix):
        self.pdfix = pdfix

    def set_page_labels(
        self,
        input_pdf,
        output_pdf,
        roman_pages_count=None,
        roman_skip=None,
        arabic_skip=None,
    ):
        if roman_skip is None:
            roman_skip = []
        if arabic_skip is None:
            arabic_skip = []

        doc = self.pdfix.OpenDoc(input_pdf, "")
        if not doc:
            raise Exception(f"Unable to open PDF: {self.pdfix.GetErrorType()}")

        try:
            num_pages = doc.GetNumPages()
            if num_pages == 0:
                raise Exception("PDF has no pages")

            if roman_pages_count is None:
                roman_pages_count = min(24, max(0, num_pages - 1))
            roman_max_num = max(0, roman_pages_count)

            root = doc.GetRootObject()
            if not root:
                raise Exception("Unable to get root object")

            page_labels_dict = root.GetDictionary("PageLabels")
            if not page_labels_dict:
                page_labels_dict = root.PutDict("PageLabels")

            nums_array = page_labels_dict.GetArray("Nums")
            if not nums_array:
                nums_array = page_labels_dict.PutArray("Nums")

            # Clear existing entries
            while nums_array.GetNumObjects() > 0:
                nums_array.RemoveNth(0)

            # 1) Cover
            nums_array.PutNumber(nums_array.GetNumObjects(), 0)
            cover_dict = nums_array.InsertDict(nums_array.GetNumObjects())
            cover_dict.PutName("Type", "PageLabel")
            cover_dict.PutString("P", "Cover")

            # 2) Roman
            roman_start_idx = 1
            current_page_idx = roman_start_idx
            current_roman_num = 1

            while current_page_idx < num_pages and current_roman_num <= roman_max_num:
                while current_roman_num in roman_skip and current_roman_num <= roman_max_num:
                    current_roman_num += 1
                if current_roman_num > roman_max_num:
                    break

                nums_array.PutNumber(nums_array.GetNumObjects(), current_page_idx)
                roman_dict = nums_array.InsertDict(nums_array.GetNumObjects())
                roman_dict.PutName("Type", "PageLabel")
                roman_dict.PutName("S", "r")
                roman_dict.PutNumber("St", current_roman_num)

                current_page_idx += 1
                current_roman_num += 1

            arabic_start_idx = current_page_idx

            # 3) Arabic
            if arabic_start_idx < num_pages:
                page_idx = arabic_start_idx
                printed_arabic = 1

                while page_idx < num_pages:
                    while printed_arabic in arabic_skip:
                        printed_arabic += 1

                    nums_array.PutNumber(nums_array.GetNumObjects(), page_idx)
                    arabic_dict = nums_array.InsertDict(nums_array.GetNumObjects())
                    arabic_dict.PutName("Type", "PageLabel")
                    arabic_dict.PutName("S", "D")
                    arabic_dict.PutNumber("St", printed_arabic)

                    page_idx += 1
                    printed_arabic += 1

            if not doc.Save(output_pdf, kSaveFull):
                raise Exception(f"Unable to save PDF: {self.pdfix.GetErrorType()}")

        finally:
            doc.Close()


def process_pdf_with_pginfo(pdfix, folder_path: str, input_pdf: str, output_pdf: str):
    merge_pginfo_files(folder_path)
    front_blank_list, other_blank_list, front_endpage = parse_pginfo(folder_path)

    setter = PageNumberSetter(pdfix)
    setter.set_page_labels(
        input_pdf=input_pdf,
        output_pdf=output_pdf,
        roman_pages_count=front_endpage,
        roman_skip=front_blank_list,
        arabic_skip=other_blank_list,
    )


# ================== FLASK API ==================
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # request size (folder_path only, so not important)

pdfix = GetPdfix()
if not pdfix:
    raise Exception("❌ Pdfix initialization failed")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "service": "page-labels"})


@app.route("/page-labels", methods=["POST"])
def page_labels():
    """
    Matches your previous working mail:

    POST http://IS-S3345:5052/page-labels
    Body -> form-data:
      folder_path = \\integraf3\\ShareYourDocuments\\CTAE\\karthi
    """
    folder_path = request.form.get("folder_path")
    if not folder_path:
        return "Error: folder_path is required", 400

    folder_path = folder_path.strip()
    if not os.path.isdir(folder_path):
        return f"Error: folder_path is not a valid directory: {folder_path}", 400

    # Find PDF inside folder (skip already labeled)
    pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
    pdf_files = [p for p in pdf_files if "_labeled" not in os.path.basename(p).lower()]
    if not pdf_files:
        return f"Error: No .pdf files found in folder: {folder_path}", 400

    pdf_files.sort()
    input_pdf = pdf_files[0]

    base, ext = os.path.splitext(os.path.basename(input_pdf))
    output_pdf = os.path.join(folder_path, f"{base}_labeled{ext}")

    try:
        process_pdf_with_pginfo(pdfix, folder_path, input_pdf, output_pdf)

        return send_file(
            output_pdf,
            as_attachment=True,
            download_name=os.path.basename(output_pdf),
            mimetype="application/pdf",
        )
    except Exception as e:
        return f"Error while processing PDF: {e}", 500


if __name__ == "__main__":
    app.run(host="IS-S3345", port=5052, debug=True)
