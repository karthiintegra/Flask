# pdfmodules/transformer.py

import os
import glob
from bs4 import BeautifulSoup
from pdfixsdk import kSaveFull

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

    print("Merged PgInfo saved:", output_path)
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

    # ---- FRONTMATTER BLANK PAGES ----
    front_blank_raw = blankpages[front_idx]       # example: "8,18,20,24"
    front_blank_list = []
    for x in front_blank_raw.split(","):
        x = x.strip()
        if x.isdigit():
            front_blank_list.append(int(x))

    # ---- OTHER BLANK PAGES ----
    other_blank_list = []
    for idx, entry in enumerate(blankpages):
        if idx == front_idx:
            continue
        for p in entry.split(","):
            p = p.strip()
            if p.isdigit():
                other_blank_list.append(int(p))

    # ---- FRONTMATTER ENDPAGE ----
    front_end_raw = endpages[front_idx]
    if not front_end_raw.isdigit():
        raise Exception(f"Frontmatter endpage is not numeric: {front_end_raw}")
    front_endpage = int(front_end_raw)

    print("\nFrontmatter blank pages:", front_blank_list)
    print("Other blank except frontmatter:", other_blank_list)
    print("Frontmatter endpage:", front_endpage)

    return front_blank_list, other_blank_list, front_endpage


def int_to_roman(num):
    """Convert integer to Roman numeral (lowercase, simple up to ~39)"""
    val = [10, 9, 5, 4, 1]
    syms = ['x', 'ix', 'v', 'iv', 'i']
    roman_num = ''
    i = 0
    while num > 0 and i < len(val):
        for _ in range(num // val[i]):
            roman_num += syms[i]
            num -= val[i]
        i += 1
    return roman_num or ""


class PageNumberSetter:
    def __init__(self, pdfix):
        self.pdfix = pdfix

    def set_page_labels(
        self,
        input_pdf,
        output_pdf,
        roman_pages_count=None,  # here treated as MAX roman number
        roman_skip=None,
        arabic_skip=None,
    ):
        """
        Page numbering rules:

        - Physical page 1 (index 0): label "Cover"
        - Roman section:
            * starts at physical page 2 (index 1)
            * printed roman numbers: 1, 2, 3, ... up to roman_pages_count
            * skip printed roman numbers in roman_skip
        - Arabic section:
            * starts on the NEXT physical page after the last roman number
            * printed arabic numbers: 1, 2, 3, ...
            * skip printed arabic numbers in arabic_skip
        """

        if roman_skip is None:
            roman_skip = []
        if arabic_skip is None:
            arabic_skip = []

        # Open the PDF document
        doc = self.pdfix.OpenDoc(input_pdf, "")
        if not doc:
            raise Exception(f"Unable to open PDF: {self.pdfix.GetErrorType()}")

        try:
            num_pages = doc.GetNumPages()

            if num_pages == 0:
                raise Exception("PDF has no pages")

            # If roman_pages_count not specified,
            # default to min(24, total-pages-minus-cover)
            if roman_pages_count is None:
                roman_pages_count = min(24, max(0, num_pages - 1))

            # Treat roman_pages_count as MAX roman number
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

            # ========= 1) Page 1 → "Cover" =========
            nums_array.PutNumber(nums_array.GetNumObjects(), 0)
            cover_dict = nums_array.InsertDict(nums_array.GetNumObjects())
            cover_dict.PutName("Type", "PageLabel")
            cover_dict.PutString("P", "Cover")

            # ========= 2) Roman section (pages 2.., printed i..roman_max_num) =========
            roman_start_idx = 1  # physical page index 1 = second page
            current_page_idx = roman_start_idx
            current_roman_num = 1  # printed roman number (i = 1)

            while (
                current_page_idx < num_pages
                and current_roman_num <= roman_max_num
            ):
                # Skip any roman numbers in roman_skip
                while current_roman_num in roman_skip and current_roman_num <= roman_max_num:
                    current_roman_num += 1

                if current_roman_num > roman_max_num:
                    break

                # Start a new label range at this page
                nums_array.PutNumber(nums_array.GetNumObjects(), current_page_idx)
                roman_dict = nums_array.InsertDict(nums_array.GetNumObjects())
                roman_dict.PutName("Type", "PageLabel")
                roman_dict.PutName("S", "r")  # lowercase roman
                roman_dict.PutNumber("St", current_roman_num)

                # Next physical page, next roman number
                current_page_idx += 1
                current_roman_num += 1

            # After loop, current_page_idx is the first physical page
            # AFTER the last roman number
            arabic_start_idx = current_page_idx

            # ========= 3) Arabic section starting at arabic_start_idx =========
            if arabic_start_idx < num_pages:
                page_idx = arabic_start_idx
                printed_arabic = 1

                while page_idx < num_pages:
                    # Skip any printed arabic numbers in arabic_skip
                    while printed_arabic in arabic_skip:
                        printed_arabic += 1

                    nums_array.PutNumber(nums_array.GetNumObjects(), page_idx)
                    arabic_dict = nums_array.InsertDict(nums_array.GetNumObjects())
                    arabic_dict.PutName("Type", "PageLabel")
                    arabic_dict.PutName("S", "D")  # decimal arabic
                    arabic_dict.PutNumber("St", printed_arabic)

                    page_idx += 1
                    printed_arabic += 1

            # Save the modified PDF
            if not doc.Save(output_pdf, kSaveFull):
                raise Exception(f"Unable to save PDF: {self.pdfix.GetErrorType()}")

            print("✅ Page numbering applied:")
            print("  - Page 1 → 'Cover'")
            if roman_max_num > 0:
                print(
                    f"  - Roman section: printed 1–{roman_max_num} (i–{int_to_roman(roman_max_num)}), "
                    f"skipping: {roman_skip}"
                )
                print(
                    f"    • Physical pages for roman section: from 2 to {arabic_start_idx}"
                )
            else:
                print("  - No Roman section")

            if arabic_start_idx < num_pages:
                print(
                    f"  - Arabic section starts at physical page {arabic_start_idx + 1} "
                    f"with printed '1', skipping: {arabic_skip}"
                )
            else:
                print("  - No Arabic section (ran out of pages)")

            print(f"  - Total physical pages: {num_pages}")

        finally:
            doc.Close()

    def verify_page_labels(self, pdf_path):
        """Verify the page labels by reading them back"""
        doc = self.pdfix.OpenDoc(pdf_path, "")
        if not doc:
            raise Exception(f"Unable to open PDF: {self.pdfix.GetErrorType()}")

        try:
            num_pages = doc.GetNumPages()
            print(f"\n📄 Document has {num_pages} pages")
            print("\nPage labels configuration:")

            root = doc.GetRootObject()
            page_labels_dict = root.GetDictionary("PageLabels")

            if page_labels_dict:
                nums_array = page_labels_dict.GetArray("Nums")
                if nums_array:
                    num_entries = nums_array.GetNumObjects()
                    print(f"Number of label ranges: {num_entries // 2}\n")

                    for i in range(0, num_entries, 2):
                        page_index = nums_array.GetInteger(i)
                        label_dict = nums_array.GetDictionary(i + 1)
                        if not label_dict:
                            continue

                        # Style
                        style_obj = label_dict.Get("S")
                        style_name = ""
                        if style_obj and hasattr(style_obj, "GetText"):
                            style_name = style_obj.GetText()

                        style_map = {
                            "r": "Lowercase Roman (i, ii, iii, ...)",
                            "R": "Uppercase Roman (I, II, III, ...)",
                            "D": "Decimal Arabic (1, 2, 3, ...)",
                            "a": "Lowercase letters (a, b, c, ...)",
                            "A": "Uppercase letters (A, B, C, ...)",
                        }
                        style_desc = style_map.get(style_name, style_name)

                        # Prefix
                        prefix = ""
                        prefix_obj = label_dict.Get("P")
                        if prefix_obj and hasattr(prefix_obj, "GetText"):
                            prefix = prefix_obj.GetText()

                        # Start value
                        start_value = label_dict.GetInteger("St", 1)

                        print(f"Range {i // 2 + 1} - Starting at physical page {page_index + 1}:")
                        if prefix:
                            print(f"  - Prefix/Label: '{prefix}'")
                        if style_desc:
                            print(f"  - Style: {style_desc}")
                        if not prefix:
                            print(f"  - Start value: {start_value}")
                        print()

        finally:
            doc.Close()


# -------------------------------------------------------------------------
# HIGH-LEVEL ENTRY POINT (USED BY FLASK)
# -------------------------------------------------------------------------
def process_pdf_with_pginfo(pdfix, folder_path: str, input_pdf: str, output_pdf: str):
    """
    1) Merge PgInfo files in folder_path
    2) Parse PgInfo → front_blank_list, other_blank_list, front_endpage
    3) Apply page labels on input_pdf and write to output_pdf
    """
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
