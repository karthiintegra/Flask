from pdfixsdk import *
import json
import re
import ctypes


# ============================================================
# CLASS 1 → Phase 1 (Steps 1–13)
# ============================================================
class PdfTagTransformerPhase1:
    """Handles steps 1–13 of the PDF tag transformation process."""

    def __init__(self, pdfix):
        self.pdfix = pdfix
        if not pdfix:
            raise Exception("❌ Pdfix initialization failed")

    # -------------------- Helper --------------------
    def jsonToRawData(self, json_dict):
        json_str = json.dumps(json_dict)
        json_data = bytearray(json_str.encode("utf-8"))
        json_data_size = len(json_str)
        json_data_raw = (ctypes.c_ubyte * json_data_size).from_buffer(json_data)
        return json_data_raw, json_data_size

    # -------------------- Step 1 --------------------
    def process_article_story(self, elem: PdsStructElement):
        st = elem.GetStructTree()
        elem = st.GetStructElementFromObject(elem.GetObject())
        if not elem:
            return

        if elem.GetType(False) == "Article":
            for i in range(elem.GetNumChildren()):
                if elem.GetChildType(i) == kPdsStructChildElement:
                    obj = elem.GetChildObject(i)
                    child = st.GetStructElementFromObject(obj)
                    if child and child.GetType(False) == "Story":
                        print("🧩 <Story> → <Sect>")
                        child.SetType("Sect")

        for i in range(elem.GetNumChildren()):
            if elem.GetChildType(i) == kPdsStructChildElement:
                self.process_article_story(st.GetStructElementFromObject(elem.GetChildObject(i)))

    def Test1_process_article_story(self, elem: PdsStructElement):
        st = elem.GetStructTree()
        elem = st.GetStructElementFromObject(elem.GetObject())
        if not elem:
            return

        if elem.GetType(False) == "Chap_affil":
            for i in range(elem.GetNumChildren()):
                if elem.GetChildType(i) == kPdsStructChildElement:
                    obj = elem.GetChildObject(i)
                    child = st.GetStructElementFromObject(obj)
                    if child and child.GetType(False) == "Span":
                        print("🧩 <Story> → <Sect>")
                        child.SetType("Test1")

        for i in range(elem.GetNumChildren()):
            if elem.GetChildType(i) == kPdsStructChildElement:
                self.Test1_process_article_story(st.GetStructElementFromObject(elem.GetChildObject(i)))


    def Test2_process_article_story(self, elem: PdsStructElement):
        st = elem.GetStructTree()
        elem = st.GetStructElementFromObject(elem.GetObject())
        if not elem:
            return

        if elem.GetType(False) == "Chap_au":
            for i in range(elem.GetNumChildren()):
                if elem.GetChildType(i) == kPdsStructChildElement:
                    obj = elem.GetChildObject(i)
                    child = st.GetStructElementFromObject(obj)
                    if child and child.GetType(False) == "Span":
                        print("🧩 <Story> → <Sect>")
                        child.SetType("Test2")

        for i in range(elem.GetNumChildren()):
            if elem.GetChildType(i) == kPdsStructChildElement:
                self.Test2_process_article_story(st.GetStructElementFromObject(elem.GetChildObject(i)))


    def chap_au_process_article_story(self, elem: PdsStructElement):
            st = elem.GetStructTree()
            elem = st.GetStructElementFromObject(elem.GetObject())
            if not elem:
                return

            if elem.GetType(False) == "Sect":
                for i in range(elem.GetNumChildren()):
                    if elem.GetChildType(i) == kPdsStructChildElement:
                        obj = elem.GetChildObject(i)
                        child = st.GetStructElementFromObject(obj)
                        if child and child.GetType(False) == "Chap_au":
                            print("🧩 <Chap_au> → <P>")
                            child.SetType("P")

            for i in range(elem.GetNumChildren()):
                if elem.GetChildType(i) == kPdsStructChildElement:
                    self.chap_au_process_article_story(st.GetStructElementFromObject(elem.GetChildObject(i)))


    def chap_affil_process_article_story(self, elem: PdsStructElement):
            st = elem.GetStructTree()
            elem = st.GetStructElementFromObject(elem.GetObject())
            if not elem:
                return

            if elem.GetType(False) == "Sect":
                for i in range(elem.GetNumChildren()):
                    if elem.GetChildType(i) == kPdsStructChildElement:
                        obj = elem.GetChildObject(i)
                        child = st.GetStructElementFromObject(obj)
                        if child and child.GetType(False) == "Chap_affil":
                            print("🧩 <Chap_affil> → <P>")
                            child.SetType("P")

            for i in range(elem.GetNumChildren()):
                if elem.GetChildType(i) == kPdsStructChildElement:
                    self.chap_affil_process_article_story(st.GetStructElementFromObject(elem.GetChildObject(i)))

    def Reftitle_process_article_story(self, elem: PdsStructElement):
            st = elem.GetStructTree()
            elem = st.GetStructElementFromObject(elem.GetObject())
            if not elem:
                return

            if elem.GetType(False) == "Sect":
                for i in range(elem.GetNumChildren()):
                    if elem.GetChildType(i) == kPdsStructChildElement:
                        obj = elem.GetChildObject(i)
                        child = st.GetStructElementFromObject(obj)
                        if child and child.GetType(False) == "Ref_title":
                            print("🧩 <Chap_affil> → <P>")
                            child.SetType("H2")

            for i in range(elem.GetNumChildren()):
                if elem.GetChildType(i) == kPdsStructChildElement:
                    self.Reftitle_process_article_story(st.GetStructElementFromObject(elem.GetChildObject(i)))

    # -------------------- Step 2 --------------------
    def process_no_paragraph_style(self, elem: PdsStructElement):
        st = elem.GetStructTree()
        elem = st.GetStructElementFromObject(elem.GetObject())
        if not elem:
            return

        if elem.GetType(False) == "_No_paragraph_style_":
            for i in range(elem.GetNumChildren()):
                if elem.GetChildType(i) == kPdsStructChildElement:
                    obj = elem.GetChildObject(i)
                    child = st.GetStructElementFromObject(obj)
                    if child and child.GetType(False) == "Span":
                        print("🧩 <Span> → <P>")
                        child.SetType("P")

        for i in range(elem.GetNumChildren()):
            if elem.GetChildType(i) == kPdsStructChildElement:
                self.process_no_paragraph_style(st.GetStructElementFromObject(elem.GetChildObject(i)))

    # -------------------- Step 3 --------------------
    def delete_tags_in_pdf(self, doc, tag_name):
        json_dict = {
            "commands": [
                {
                    "name": "delete_tags",
                    "params": [
                        {"name": "tag_names", "value": tag_name},
                        {"name": "exclude_tag_names", "value": "false"},
                        {"name": "skip_tag_names", "value": ""},
                        {"name": "flags", "value": 255},
                        {"name": "tag_content", "value": "move"},
                    ],
                }
            ]
        }

        json_data, json_size = self.jsonToRawData(json_dict)
        memStm = self.pdfix.CreateMemStream()
        memStm.Write(0, json_data, json_size)
        command = doc.GetCommand()
        command.LoadParamsFromStream(memStm, kDataFormatJson)
        memStm.Destroy()

        print(f"🗑️ Removing <{tag_name}>...")
        if not command.Run():
            raise Exception("❌ Failed to delete tags: " + self.pdfix.GetError())

    # ============================================================
    # 4️⃣ Move (1) text node into <Figure> under <Eq_num>
    # ============================================================
    def move_number_into_figure(self, elem: PdsStructElement):
        st = elem.GetStructTree()
        elem = st.GetStructElementFromObject(elem.GetObject())
        if not elem:
            return
        if elem.GetType(False) == "Eq_num":
            figure_elem, number_index = None, -1
            for i in range(elem.GetNumChildren()):
                ctype, cobj = elem.GetChildType(i), elem.GetChildObject(i)
                if ctype != kPdsStructChildElement:
                    number_index = i
                    continue
                child = st.GetStructElementFromObject(cobj)
                if child and child.GetType(False) == "Figure":
                    figure_elem = child
            if figure_elem and number_index != -1:
                eq_ref = st.GetStructElementFromObject(elem.GetObject())
                fig_ref = st.GetStructElementFromObject(figure_elem.GetObject())
                if eq_ref and fig_ref:
                    eq_ref.MoveChild(number_index, fig_ref, -1)
                    print("✅ Moved (1) into Figure")
        for i in range(elem.GetNumChildren()):
            if elem.GetChildType(i) == kPdsStructChildElement:
                self.move_number_into_figure(st.GetStructElementFromObject(elem.GetChildObject(i)))

    # ============================================================
    # 5️⃣ Move space nodes from Eq_num → previous <P>
    # ============================================================
    def _is_whitespace_struct(self, elem: PdsStructElement) -> bool:
        try:
            txt = elem.GetText(True)
            return txt is not None and txt.strip() == ""
        except Exception:
            return False

    def _move_kid(self, eq_elem, kid_index, dest_p):
        st = eq_elem.GetStructTree()
        fresh_eq = st.GetStructElementFromObject(eq_elem.GetObject())
        fresh_dest = st.GetStructElementFromObject(dest_p.GetObject())
        if not (fresh_eq and fresh_dest):
            return
        if not fresh_eq.MoveChild(kid_index, fresh_dest, -1):
            cobj = fresh_eq.GetChildObject(kid_index)
            if cobj:
                fresh_dest.AddKidObject(cobj, -1)
                fresh_eq.RemoveChild(kid_index)

    def _move_space_from_eqnum_to_previous_p(self, grand):
        st = grand.GetStructTree()
        grand = st.GetStructElementFromObject(grand.GetObject())
        if not grand:
            return
        last_p_elem = None
        for i in range(grand.GetNumChildren()):
            if grand.GetChildType(i) != kPdsStructChildElement:
                continue
            cobj = grand.GetChildObject(i)
            child = st.GetStructElementFromObject(cobj)
            if not child:
                continue
            tag = child.GetType(False)
            if tag == "P":
                last_p_elem = child
            elif tag == "Eq_num" and last_p_elem:
                candidates = []
                for k in range(child.GetNumChildren()):
                    ktype = child.GetChildType(k)
                    if ktype in (kPdsStructChildPageContent, kPdsStructChildStreamContent):
                        candidates.append(k)
                    elif ktype == kPdsStructChildElement:
                        s_elem = st.GetStructElementFromObject(child.GetChildObject(k))
                        if s_elem and self._is_whitespace_struct(s_elem):
                            candidates.append(k)
                for idx in reversed(candidates):
                    self._move_kid(child, idx, last_p_elem)
                    print("🪶 Moved space into preceding <P>")

    def traverse(self, elem):
        self._move_space_from_eqnum_to_previous_p(elem)
        for i in range(elem.GetNumChildren()):
            if elem.GetChildType(i) == kPdsStructChildElement:
                self.traverse(elem.GetStructTree().GetStructElementFromObject(elem.GetChildObject(i)))

    # ============================================================
    # 6️⃣ Rename <Figure> → <Formula> under <Eq_num>
    # ============================================================
    def rename_figure_to_formula(self, elem):
        st = elem.GetStructTree()
        elem = st.GetStructElementFromObject(elem.GetObject())
        if not elem:
            return
        if elem.GetType(False) == "Eq_num":
            for i in range(elem.GetNumChildren()):
                if elem.GetChildType(i) == kPdsStructChildElement:
                    child = st.GetStructElementFromObject(elem.GetChildObject(i))
                    if child and child.GetType(False) == "Figure":
                        print("🧩 <Figure> → <Formula>")
                        child.SetType("Formula")
        for i in range(elem.GetNumChildren()):
            if elem.GetChildType(i) == kPdsStructChildElement:
                self.rename_figure_to_formula(st.GetStructElementFromObject(elem.GetChildObject(i)))

    # ============================================================
    # 7️⃣ Delete <Article> and 8️⃣ Delete <Eq_num>
    # ============================================================
    def delete_article_tags(self, doc):
        self.delete_tags_in_pdf(doc, "Article")

    def delete_eqnum_tags(self, doc):
        self.delete_tags_in_pdf(doc, "Eq_num")

    # ============================================================
    # 9️⃣ Rename <_Figure_> → <__Figure__> inside <Story>
    # ============================================================
    def rename_nested_figure(self, elem: PdsStructElement):
        if elem.GetType(False) == "Story":
            for i in range(elem.GetNumChildren()):
                if elem.GetChildType(i) != kPdsStructChildElement:
                    continue
                obj = elem.GetChildObject(i)
                child_elem = elem.GetStructTree().GetStructElementFromObject(obj)
                if not child_elem:
                    continue
                if child_elem.GetType(False) == "_Figure_":
                    for j in range(child_elem.GetNumChildren()):
                        if child_elem.GetChildType(j) == kPdsStructChildElement:
                            sub_obj = child_elem.GetChildObject(j)
                            sub_elem = child_elem.GetStructTree().GetStructElementFromObject(sub_obj)
                            if sub_elem and sub_elem.GetType(False) == "Figure":
                                print("🧩 <_Figure_> → <__Figure__>")
                                child_elem.SetType("__Figure__")
                                break

        for i in range(elem.GetNumChildren()):
            if elem.GetChildType(i) == kPdsStructChildElement:
                self.rename_nested_figure(elem.GetStructTree().GetStructElementFromObject(elem.GetChildObject(i)))

    # ============================================================
    # 🔟 Wrap <Story> content into <lb1l> if it has <__Figure__>
    # ============================================================
    def wrap_story_with_lb1l(self, elem: PdsStructElement):
        if elem.GetType(False) == "Story":
            contains_double_fig = any(
                elem.GetStructTree().GetStructElementFromObject(elem.GetChildObject(i)).GetType(False) == "__Figure__"
                for i in range(elem.GetNumChildren())
                if elem.GetChildType(i) == kPdsStructChildElement
            )

            if contains_double_fig:
                print("🧩 Wrapping <Story> content into <lb1l>")
                num_children = elem.GetNumChildren()
                if num_children == 0:
                    return
                lbl_elem = elem.AddNewChild("lb1l", 0)
                for _ in range(num_children):
                    if elem.GetNumChildren() > 1:
                        elem.MoveChild(1, lbl_elem, -1)

        for i in range(elem.GetNumChildren()):
            if elem.GetChildType(i) == kPdsStructChildElement:
                self.wrap_story_with_lb1l(elem.GetStructTree().GetStructElementFromObject(elem.GetChildObject(i)))

    # ============================================================
    # 1️⃣1️⃣ Move <Figure> out of <__Figure__> to parent
    # ============================================================
    def move_figure_out_of_double_figure(self, elem: PdsStructElement, parent: PdsStructElement = None):
        if elem.GetType(False) == "__Figure__":
            st = elem.GetStructTree()
            for i in range(elem.GetNumChildren()):
                if elem.GetChildType(i) != kPdsStructChildElement:
                    continue
                obj = elem.GetChildObject(i)
                child_elem = st.GetStructElementFromObject(obj)
                if not child_elem:
                    continue

                if child_elem.GetType(False) == "Figure" and parent is not None:
                    print("🪄 Found <Figure> inside <__Figure__>, moving it up to parent...")
                    fresh_parent = st.GetStructElementFromObject(parent.GetObject())
                    fresh_elem = st.GetStructElementFromObject(elem.GetObject())
                    if fresh_parent and fresh_elem:
                        fresh_elem.MoveChild(i, fresh_parent, -1)
                        print("✅ Figure moved to parent successfully")
                    return

        for i in range(elem.GetNumChildren()):
            if elem.GetChildType(i) == kPdsStructChildElement:
                self.move_figure_out_of_double_figure(
                    elem.GetStructTree().GetStructElementFromObject(elem.GetChildObject(i)),
                    elem)

    # ============================================================
    # 1️⃣2️⃣ Move <__Figure__> under <Figure>
    # ============================================================
    def move_caption_under_figure(self, elem: PdsStructElement, parent: PdsStructElement = None):
        if parent is not None:
            caption_index = -1
            figure_index = -1
            caption_elem = None
            figure_elem = None

            for i in range(parent.GetNumChildren()):
                if parent.GetChildType(i) != kPdsStructChildElement:
                    continue

                obj = parent.GetChildObject(i)
                child = parent.GetStructTree().GetStructElementFromObject(obj)
                if not child:
                    continue

                if child.GetType(False) == "__Figure__":
                    caption_index = i
                    caption_elem = child
                elif child.GetType(False) == "Figure":
                    figure_index = i
                    figure_elem = child

            if caption_elem is not None and figure_elem is not None:
                if caption_index < figure_index:
                    figure_index -= 1
                parent.MoveChild(caption_index, figure_elem, -1)
                print("✅ <__Figure__> moved under <Figure>")

        for i in range(elem.GetNumChildren()):
            if elem.GetChildType(i) == kPdsStructChildElement:
                self.move_caption_under_figure(elem.GetStructTree().GetStructElementFromObject(elem.GetChildObject(i)),
                                               elem)

    # ============================================================
    # 1️⃣3️⃣ Add <P> inside <__Figure__> under <Figure>
    # ============================================================
    def add_p_inside_caption(self, elem: PdsStructElement):
        if elem.GetType(False) == "Figure":
            for i in range(elem.GetNumChildren()):
                if elem.GetChildType(i) != kPdsStructChildElement:
                    continue
                obj = elem.GetChildObject(i)
                child_elem = elem.GetStructTree().GetStructElementFromObject(obj)
                if not child_elem:
                    continue
                if child_elem.GetType(False) == "__Figure__":
                    print("🪄 Found <__Figure__> inside <Figure>")
                    num_children = child_elem.GetNumChildren()
                    if num_children == 0:
                        print("⚠️ Caption is empty")
                        continue
                    p_elem = child_elem.AddNewChild("P", -1)
                    for _ in range(num_children):
                        child_elem.MoveChild(0, p_elem, -1)
                    print(f"✅ Moved {num_children} children into new <P> under Caption")

        for i in range(elem.GetNumChildren()):
            if elem.GetChildType(i) == kPdsStructChildElement:
                self.add_p_inside_caption(elem.GetStructTree().GetStructElementFromObject(elem.GetChildObject(i)))

    # -------------------- Run All Steps --------------------
    def modify_pdf_tags(self, input_path, output_path):
        doc = self.pdfix.OpenDoc(input_path, "")
        if not doc:
            raise Exception("❌ Failed to open PDF")

        st = doc.GetStructTree()
        if not st:
            raise Exception("❌ No structure tree found")

        print("🚀 Starting Phase 1 transformations...")

        for i in range(st.GetNumChildren()):
            elem = st.GetStructElementFromObject(st.GetChildObject(i))
            if elem:
                self.process_article_story(elem)
                # self.Test1_process_article_story(elem)
                # self.Test2_process_article_story(elem)
                self.chap_au_process_article_story(elem)
                self.chap_affil_process_article_story(elem)
                self.Reftitle_process_article_story(elem)
                # self.process_no_paragraph_style(elem)
                # self.move_number_into_figure(elem)
                # self.traverse(elem)
                # self.rename_figure_to_formula(elem)
                self.rename_nested_figure(elem)
                self.wrap_story_with_lb1l(elem)
                self.move_figure_out_of_double_figure(elem)
                self.move_caption_under_figure(elem)
                # self.add_p_inside_caption(elem)

        self.delete_tags_in_pdf(doc, "Article")
        self.delete_tags_in_pdf(doc, "Test1")
        self.delete_tags_in_pdf(doc, "Test2")
        # self.delete_tags_in_pdf(doc, "_No_paragraph_style_")
        # self.delete_tags_in_pdf(doc, "Eq_num")

        if not doc.Save(output_path, kSaveFull):
            raise Exception(f"❌ Failed to save PDF: {self.pdfix.GetError()}")

        doc.Close()
        print(f"✅ Phase 1 complete. Saved to: {output_path}")


# ============================================================
# CLASS 2 → Phase 2 (Future Steps 14–30)
# ============================================================
class Reference:
    """Handles Steps 14–30 (new operations)."""

    def __init__(self, pdfix):
        self.pdfix = pdfix

    def step14_move_references_p_to_l(self, elem: PdsStructElement, parent: PdsStructElement = None):
        """Step 14: Find <H2> tag with 'References' and move all following <P> tags under new <L> tag."""
        st = elem.GetStructTree()
        fresh_elem = st.GetStructElementFromObject(elem.GetObject())
        if not fresh_elem:
            return

        # ✅ Step 1: Detect H2 tag with "References"
        if fresh_elem.GetType(False) == "H2":
            text_content = fresh_elem.GetText(True)
            if text_content and text_content.strip().lower() == "references":
                print("📘 Found 'References' H2 tag — collecting following <P> tags...")

                if parent:
                    start_index = None

                    # Find index of the H2 tag within its parent
                    for i in range(parent.GetNumChildren()):
                        if parent.GetChildType(i) != kPdsStructChildElement:
                            continue
                        obj = parent.GetChildObject(i)
                        sibling = st.GetStructElementFromObject(obj)
                        if sibling and sibling.GetObject().obj == fresh_elem.GetObject().obj:
                            start_index = i
                            break

                    if start_index is not None:
                        # ✅ Create new <L> tag right after <H2>
                        l_elem = parent.AddNewChild("L", start_index + 1)
                        l_struct = st.GetStructElementFromObject(l_elem.GetObject())

                        if not l_struct:
                            print("⚠️ Failed to create <L> tag")
                            return

                        print("🧩 Created <L> tag for reference paragraphs")

                        # ✅ Keep moving <P> tags after <H2> dynamically until none remain
                        moved_count = 0
                        while True:
                            moved = False
                            total_children = parent.GetNumChildren()

                            for j in range(start_index + 1, total_children):
                                if parent.GetChildType(j) != kPdsStructChildElement:
                                    continue
                                obj = parent.GetChildObject(j)
                                sibling = st.GetStructElementFromObject(obj)
                                if sibling and sibling.GetType(False) == "P":
                                    parent.MoveChild(j, l_struct, -1)
                                    moved_count += 1
                                    moved = True
                                    break  # restart after move to update structure

                            if not moved:
                                break  # stop when no more <P> remain

                        print(f"✅ Moved {moved_count} <P> tags under new <L>")

        # ✅ Step 2: Continue recursion
        for i in range(fresh_elem.GetNumChildren()):
            if fresh_elem.GetChildType(i) == kPdsStructChildElement:
                obj = fresh_elem.GetChildObject(i)
                child_elem = st.GetStructElementFromObject(obj)
                if child_elem:
                    self.step14_move_references_p_to_l(child_elem,
                                                       fresh_elem)  # your future logic for deleting Story and lb1l

    def step15_wrap_p_into_li(self, elem: PdsStructElement):
        """Step 15: Wrap all <P> tags under <L> into a single <LI> tag."""
        st = elem.GetStructTree()
        fresh_elem = st.GetStructElementFromObject(elem.GetObject())
        if not fresh_elem:
            return

        # ✅ Identify <L> tags
        if fresh_elem.GetType(False) == "L":
            print("🧩 Found <L> tag — wrapping its content into <LI>")

            num_children = fresh_elem.GetNumChildren()
            if num_children == 0:
                return

            # ✅ Create new <LI> tag at the beginning
            li_elem = fresh_elem.AddNewChild("LI", 0)
            li_struct = st.GetStructElementFromObject(li_elem.GetObject())
            if not li_struct:
                print("⚠️ Failed to create <LI> tag")
                return

            moved_count = 0
            # ✅ Move all existing children (except the newly created <LI>) into it
            # Always move index 1, since index 0 is the new <LI> itself
            while fresh_elem.GetNumChildren() > 1:
                fresh_elem.MoveChild(1, li_struct, -1)
                moved_count += 1

            print(f"✅ Moved {moved_count} children into <LI> under <L>")

        # ✅ Recurse into children
        for i in range(fresh_elem.GetNumChildren()):
            if fresh_elem.GetChildType(i) == kPdsStructChildElement:
                obj = fresh_elem.GetChildObject(i)
                child_elem = st.GetStructElementFromObject(obj)
                if child_elem:
                    self.step15_wrap_p_into_li(child_elem)

    def step16_rename_p_to_lbody_in_li(self, elem: PdsStructElement):
        """Step 16: Inside each <LI> tag, rename <P> to <LBody>."""
        st = elem.GetStructTree()
        fresh_elem = st.GetStructElementFromObject(elem.GetObject())
        if not fresh_elem:
            return

        # ✅ If current element is <LI>
        if fresh_elem.GetType(False) == "LI":
            print("🧩 Found <LI> tag — converting <P> to <LBody>")
            for i in range(fresh_elem.GetNumChildren()):
                if fresh_elem.GetChildType(i) != kPdsStructChildElement:
                    continue
                obj = fresh_elem.GetChildObject(i)
                child_elem = st.GetStructElementFromObject(obj)
                if not child_elem:
                    continue

                if child_elem.GetType(False) == "P":
                    print("🔹 Found <P> under <LI> — renaming to <LBody>")
                    child_elem.SetType("LBody")

        # ✅ Recursively process all descendants
        for i in range(fresh_elem.GetNumChildren()):
            if fresh_elem.GetChildType(i) == kPdsStructChildElement:
                obj = fresh_elem.GetChildObject(i)
                child_elem = st.GetStructElementFromObject(obj)
                if child_elem:
                    self.step16_rename_p_to_lbody_in_li(child_elem)  # move T_credit tag under Table logic

    def step17_split_multiple_lbody_in_li(self, elem: PdsStructElement):
        """Step 17: If an <LI> has multiple <LBody> children, move each into its own <LI>."""
        st = elem.GetStructTree()
        fresh_elem = st.GetStructElementFromObject(elem.GetObject())
        if not fresh_elem:
            return

        # ✅ Only process <L> tags
        if fresh_elem.GetType(False) == "L":
            print("🔍 Processing <L> structure...")

            # Collect LI children
            li_indices = []
            for i in range(fresh_elem.GetNumChildren()):
                if fresh_elem.GetChildType(i) == kPdsStructChildElement:
                    obj = fresh_elem.GetChildObject(i)
                    child = st.GetStructElementFromObject(obj)
                    if child and child.GetType(False) == "LI":
                        li_indices.append(i)

            # ✅ Process each <LI>
            for li_index in reversed(li_indices):
                li_obj = fresh_elem.GetChildObject(li_index)
                li_elem = st.GetStructElementFromObject(li_obj)
                if not li_elem:
                    continue

                # Find all <LBody> children
                lbody_indices = []
                for j in range(li_elem.GetNumChildren()):
                    if li_elem.GetChildType(j) == kPdsStructChildElement:
                        obj = li_elem.GetChildObject(j)
                        child = st.GetStructElementFromObject(obj)
                        if child and child.GetType(False) == "LBody":
                            lbody_indices.append(j)

                # ✅ If multiple LBodies — split them
                if len(lbody_indices) > 1:
                    print(f"🧩 Found <LI> with {len(lbody_indices)} <LBody> — splitting...")

                    # Move each LBody (except the first) into a new <LI>
                    for idx in reversed(lbody_indices[1:]):
                        lbody_obj = li_elem.GetChildObject(idx)
                        if not lbody_obj:
                            continue

                        # Create a new LI right after the current one
                        new_li = fresh_elem.AddNewChild("LI", li_index + 1)
                        new_li_elem = st.GetStructElementFromObject(new_li.GetObject())
                        if not new_li_elem:
                            continue

                        # Move the LBody into the new LI
                        li_elem.MoveChild(idx, new_li_elem, -1)
                        print("✅ Moved one <LBody> into new <LI>")

        # ✅ Recurse through children
        for i in range(fresh_elem.GetNumChildren()):
            if fresh_elem.GetChildType(i) == kPdsStructChildElement:
                obj = fresh_elem.GetChildObject(i)
                child_elem = st.GetStructElementFromObject(obj)
                if child_elem:
                    self.step17_split_multiple_lbody_in_li(child_elem)

    def modify_pdf_tags(self, input_path, output_path):
        doc = self.pdfix.OpenDoc(input_path, "")
        if not doc:
            raise Exception("❌ Failed to open PDF")

        st = doc.GetStructTree()
        print("🚀 Starting Phase 2 transformations...")

        for i in range(st.GetNumChildren()):
            elem = st.GetStructElementFromObject(st.GetChildObject(i))
            if elem:
                self.step14_move_references_p_to_l(elem)
                self.step15_wrap_p_into_li(elem)
                self.step16_rename_p_to_lbody_in_li(elem)
                self.step17_split_multiple_lbody_in_li(elem)

        if not doc.Save(output_path, kSaveFull):
            raise Exception(f"❌ Failed to save: {self.pdfix.GetError()}")

        doc.Close()
        print(f"✅ Phase 2 complete. Saved to: {output_path}")


class Table:
    """Handles Steps 14–30 (new operations)."""

    def __init__(self, pdfix):
        self.pdfix = pdfix

    def step18_fix_table_structure(self, elem: PdsStructElement):
        """Detect <Table> tags and split TRs into <THead> and <TBody>."""
        st = elem.GetStructTree()
        fresh_elem = st.GetStructElementFromObject(elem.GetObject())
        if not fresh_elem:
            return

        # ✅ Process only <Table> elements
        if fresh_elem.GetType(False) == "Table":
            print("📊 Found <Table> — restructuring TRs into <THead> and <TBody>")

            # Collect <TR> references
            tr_elems = []
            for i in range(fresh_elem.GetNumChildren()):
                if fresh_elem.GetChildType(i) == kPdsStructChildElement:
                    obj = fresh_elem.GetChildObject(i)
                    child = st.GetStructElementFromObject(obj)
                    if child and child.GetType(False) == "TR":
                        tr_elems.append(child)

            if len(tr_elems) > 1:
                # ✅ Create <THead> and <TBody> at the end
                thead = fresh_elem.AddNewChild("THead", -1)
                tbody = fresh_elem.AddNewChild("TBody", -1)

                thead_elem = st.GetStructElementFromObject(thead.GetObject())
                tbody_elem = st.GetStructElementFromObject(tbody.GetObject())

                if not thead_elem or not tbody_elem:
                    print("⚠️ Failed to create <THead> or <TBody>")
                    return

                print(f"🧩 Created <THead> and <TBody> under <Table> with {len(tr_elems)} TRs")

                # ✅ Move first TR into <THead>
                first_tr_obj = tr_elems[0].GetObject()
                for i in range(fresh_elem.GetNumChildren()):
                    if fresh_elem.GetChildType(i) != kPdsStructChildElement:
                        continue
                    obj = fresh_elem.GetChildObject(i)
                    if obj.obj == first_tr_obj.obj:
                        fresh_elem.MoveChild(i, thead_elem, -1)
                        print("✅ Moved first <TR> into <THead>")
                        break

                # ✅ Move remaining TRs into <TBody>
                moved_count = 0
                while True:
                    moved = False
                    for i in range(fresh_elem.GetNumChildren()):
                        if fresh_elem.GetChildType(i) != kPdsStructChildElement:
                            continue
                        obj = fresh_elem.GetChildObject(i)
                        child = st.GetStructElementFromObject(obj)
                        if child and child.GetType(False) == "TR":
                            fresh_elem.MoveChild(i, tbody_elem, -1)
                            moved_count += 1
                            moved = True
                            break
                    if not moved:
                        break

                print(f"✅ Moved remaining {moved_count} <TR> tags into <TBody>")

        # ✅ Recurse deeper
        for i in range(fresh_elem.GetNumChildren()):
            if fresh_elem.GetChildType(i) == kPdsStructChildElement:
                obj = fresh_elem.GetChildObject(i)
                child_elem = st.GetStructElementFromObject(obj)
                if child_elem:
                    self.step18_fix_table_structure(child_elem)

    def step19_move_tcredit_under_table(self, elem: PdsStructElement):
        st = elem.GetStructTree()
        fresh_elem = st.GetStructElementFromObject(elem.GetObject())
        if not fresh_elem:
            return

        # ✅ Only process <Story> elements
        if fresh_elem.GetType(False) == "Story":
            figure_elem = None
            tcredit_elem = None

            # 1️⃣ Find <_Figure_> and <T_credit>
            for i in range(fresh_elem.GetNumChildren()):
                if fresh_elem.GetChildType(i) != kPdsStructChildElement:
                    continue

                obj = fresh_elem.GetChildObject(i)
                child = st.GetStructElementFromObject(obj)
                if not child:
                    continue

                tag = child.GetType(False)
                if tag == "_Figure_":
                    figure_elem = child
                elif tag == "T_credit":
                    tcredit_elem = child

            # 2️⃣ If both are found
            if figure_elem and tcredit_elem:
                table_elem = None
                for j in range(figure_elem.GetNumChildren()):
                    if figure_elem.GetChildType(j) == kPdsStructChildElement:
                        obj = figure_elem.GetChildObject(j)
                        child = st.GetStructElementFromObject(obj)
                        if child and child.GetType(False) == "Table":
                            table_elem = child
                            break

                # 3️⃣ Move <T_credit> into <Table>
                if table_elem:
                    print("🧩 Found <Story> with <_Figure_> + <Table> + sibling <T_credit>")
                    print("   Moving <T_credit> into <Table>...")

                    fresh_story = st.GetStructElementFromObject(fresh_elem.GetObject())
                    table_fresh = st.GetStructElementFromObject(table_elem.GetObject())

                    for i in range(fresh_story.GetNumChildren()):
                        if fresh_story.GetChildType(i) != kPdsStructChildElement:
                            continue
                        obj = fresh_story.GetChildObject(i)
                        if obj.obj == tcredit_elem.GetObject().obj:
                            fresh_story.MoveChild(i, table_fresh, -1)
                            print("✅ <T_credit> moved inside <Table>")
                            break

        # 4️⃣ Recurse into child elements
        for i in range(fresh_elem.GetNumChildren()):
            if fresh_elem.GetChildType(i) == kPdsStructChildElement:
                obj = fresh_elem.GetChildObject(i)
                child_elem = st.GetStructElementFromObject(obj)
                if child_elem:
                    self.step19_move_tcredit_under_table(child_elem)

    def step20_move_table_out_of_figure(self, elem: PdsStructElement, parent: PdsStructElement = None):
        """
        Move <Table> from inside <_Figure_> up one level to become a sibling under <Story>.
        """
        st = elem.GetStructTree()
        fresh_elem = st.GetStructElementFromObject(elem.GetObject())
        if not fresh_elem:
            return

        # ✅ Process <Story> elements
        if fresh_elem.GetType(False) == "Story":
            for i in range(fresh_elem.GetNumChildren()):
                if fresh_elem.GetChildType(i) != kPdsStructChildElement:
                    continue

                obj = fresh_elem.GetChildObject(i)
                child = st.GetStructElementFromObject(obj)
                if not child:
                    continue

                # Check for <_Figure_> inside <Story>
                if child.GetType(False) == "_Figure_":
                    figure_elem = child
                    table_elem = None

                    # Find <Table> inside <_Figure_>
                    for j in range(figure_elem.GetNumChildren()):
                        if figure_elem.GetChildType(j) != kPdsStructChildElement:
                            continue
                        obj2 = figure_elem.GetChildObject(j)
                        sub_child = st.GetStructElementFromObject(obj2)
                        if sub_child and sub_child.GetType(False) == "Table":
                            table_elem = sub_child
                            break

                    # ✅ Move <Table> under <Story> (make sibling of <_Figure_>)
                    if table_elem:
                        print("🧩 Found <_Figure_> with <Table> inside — moving <Table> to <Story>")

                        # Get stable references
                        fresh_story = st.GetStructElementFromObject(fresh_elem.GetObject())
                        fresh_table = st.GetStructElementFromObject(table_elem.GetObject())

                        # Find <Table> index inside <_Figure_> and move it
                        for k in range(figure_elem.GetNumChildren()):
                            if figure_elem.GetChildType(k) != kPdsStructChildElement:
                                continue
                            obj3 = figure_elem.GetChildObject(k)
                            if obj3.obj == table_elem.GetObject().obj:
                                figure_elem.MoveChild(k, fresh_story, -1)
                                print("✅ <Table> moved to <Story> successfully")
                                break

        # ✅ Continue recursion
        for i in range(fresh_elem.GetNumChildren()):
            if fresh_elem.GetChildType(i) == kPdsStructChildElement:
                obj = fresh_elem.GetChildObject(i)
                child_elem = st.GetStructElementFromObject(obj)
                if child_elem:
                    self.step20_move_table_out_of_figure(child_elem, fresh_elem)

    def step21_move_figure_into_table(self, elem: PdsStructElement, parent: PdsStructElement = None):
        """
        Step 21️⃣ — Move <_Figure_> into <Table> under <Story>.
        """
        st = elem.GetStructTree()
        fresh_elem = st.GetStructElementFromObject(elem.GetObject())
        if not fresh_elem:
            return

        # ✅ Process only <Story> tags
        if fresh_elem.GetType(False) == "Story":
            figure_elem = None
            table_elem = None

            # Find both <_Figure_> and <Table> inside <Story>
            for i in range(fresh_elem.GetNumChildren()):
                if fresh_elem.GetChildType(i) != kPdsStructChildElement:
                    continue
                obj = fresh_elem.GetChildObject(i)
                child = st.GetStructElementFromObject(obj)
                if not child:
                    continue

                tag_type = child.GetType(False)
                if tag_type == "_Figure_":
                    figure_elem = child
                elif tag_type == "Table":
                    table_elem = child

            # ✅ Move <_Figure_> into <Table> (if both exist)
            if figure_elem and table_elem:
                print("🧩 Found <Story> with <_Figure_> and <Table> — moving <_Figure_> inside <Table>")

                # Find <_Figure_> index in <Story>
                figure_obj = figure_elem.GetObject()
                for idx in range(fresh_elem.GetNumChildren()):
                    if fresh_elem.GetChildType(idx) != kPdsStructChildElement:
                        continue
                    obj = fresh_elem.GetChildObject(idx)
                    if obj.obj == figure_obj.obj:
                        # ✅ Move it to the beginning of <Table>
                        fresh_elem.MoveChild(idx, table_elem, 0)
                        print("✅ <_Figure_> moved into <Table>")
                        break

        # ✅ Recurse through structure tree
        for i in range(fresh_elem.GetNumChildren()):
            if fresh_elem.GetChildType(i) == kPdsStructChildElement:
                obj = fresh_elem.GetChildObject(i)
                child_elem = st.GetStructElementFromObject(obj)
                if child_elem:
                    self.step21_move_figure_into_table(child_elem, fresh_elem)

    def step22_change_Figure_to_Caption(self, elem: PdsStructElement):
        st = elem.GetStructTree()
        elem = st.GetStructElementFromObject(elem.GetObject())
        if not elem:
            return

        if elem.GetType(False) == "Table":
            for i in range(elem.GetNumChildren()):
                if elem.GetChildType(i) == kPdsStructChildElement:
                    obj = elem.GetChildObject(i)
                    child = st.GetStructElementFromObject(obj)
                    if child and child.GetType(False) == "_Figure_":
                        print("🧩 <_Figure_> → <Sect>")
                        child.SetType("Caption")

                    if child and child.GetType(False) == "T_credit":
                        print("🧩 <T_credit> → <T_credit>")
                        child.SetType("TFoot")

        for i in range(elem.GetNumChildren()):
            if elem.GetChildType(i) == kPdsStructChildElement:
                self.step22_change_Figure_to_Caption(st.GetStructElementFromObject(elem.GetChildObject(i)))

    def step23_delete_story_if_only_table(self, elem: PdsStructElement, parent: PdsStructElement = None):
        """
        Step 23️⃣ — If <Story> has only one child <Table>, remove <Story> and keep <Table> under its parent.
        """
        st = elem.GetStructTree()
        fresh_elem = st.GetStructElementFromObject(elem.GetObject())
        if not fresh_elem:
            return

        # Only process <Story> tags
        if fresh_elem.GetType(False) == "Story" and parent:
            child_elements = []
            for i in range(fresh_elem.GetNumChildren()):
                if fresh_elem.GetChildType(i) == kPdsStructChildElement:
                    obj = fresh_elem.GetChildObject(i)
                    child = st.GetStructElementFromObject(obj)
                    if child:
                        child_elements.append(child)

            # ✅ Check if Story has exactly 1 child, and that child is <Table>
            if len(child_elements) == 1 and child_elements[0].GetType(False) == "Table":
                print("🧩 <Story> has only <Table> — deleting <Story> and keeping <Table>")

                # Get both Story and Table as fresh references
                story_ref = fresh_elem
                table_ref = child_elements[0]

                # Find Story in its parent, then move Table out and delete Story
                for i in range(parent.GetNumChildren()):
                    if parent.GetChildType(i) != kPdsStructChildElement:
                        continue

                    obj = parent.GetChildObject(i)
                    if obj.obj == story_ref.GetObject().obj:
                        # Move <Table> into parent's child list (next position)
                        story_ref.MoveChild(0, parent, i + 1)

                        # Remove Story
                        parent.RemoveChild(i)
                        print("✅ <Table> successfully moved outside <Story>")
                        return

        # ✅ Recurse through the structure
        for i in range(fresh_elem.GetNumChildren()):
            if fresh_elem.GetChildType(i) == kPdsStructChildElement:
                obj = fresh_elem.GetChildObject(i)
                child_elem = st.GetStructElementFromObject(obj)
                if child_elem:
                    self.step23_delete_story_if_only_table(child_elem, fresh_elem)

    def step24_move_table_before_heading(self, elem: PdsStructElement, parent: PdsStructElement = None):
        st = elem.GetStructTree()
        fresh = st.GetStructElementFromObject(elem.GetObject())
        if not fresh:
            return

        # ✅ Process only <P> tags
        if fresh.GetType(False) == "P":
            table_index = None
            for i in range(fresh.GetNumChildren()):
                if fresh.GetChildType(i) == kPdsStructChildElement:
                    obj = fresh.GetChildObject(i)
                    child = st.GetStructElementFromObject(obj)
                    if child and child.GetType(False) == "Table":
                        table_index = i
                        break

            # ✅ Found <Table> inside <P>
            if table_index is not None and parent:
                p_index = None

                # Find index of <P> in its parent
                for i in range(parent.GetNumChildren()):
                    if parent.GetChildObject(i).obj == fresh.GetObject().obj:
                        p_index = i
                        break

                # ✅ Ensure <P> has previous sibling
                if p_index is not None and p_index > 0:
                    prev_obj = parent.GetChildObject(p_index - 1)
                    prev_elem = st.GetStructElementFromObject(prev_obj)

                    # ✅ If previous sibling is heading → move table
                    if prev_elem and prev_elem.GetType(False) in ["H1", "H2", "H3", "H4", "H5", "H6"]:
                        print("📦 Moving <Table> above heading...")

                        # Refresh objects before modifying structure
                        fresh_p = st.GetStructElementFromObject(fresh.GetObject())
                        fresh_parent = st.GetStructElementFromObject(parent.GetObject())
                        table_elem = st.GetStructElementFromObject(fresh_p.GetChildObject(table_index))

                        # ✅ Move table to parent at new position
                        fresh_p.MoveChild(table_index, fresh_parent, p_index - 1)

                        print("✅ <Table> moved successfully!")

        # ✅ Recursively continue
        for i in range(fresh.GetNumChildren()):
            if fresh.GetChildType(i) == kPdsStructChildElement:
                child = st.GetStructElementFromObject(fresh.GetChildObject(i))
                if child:
                    self.step24_move_table_before_heading(child, fresh)

    def modify_pdf_tags(self, input_path, output_path):
        doc = self.pdfix.OpenDoc(input_path, "")
        if not doc:
            raise Exception("❌ Failed to open PDF")

        st = doc.GetStructTree()
        print("🚀 Starting Phase 2 transformations...")

        for i in range(st.GetNumChildren()):
            elem = st.GetStructElementFromObject(st.GetChildObject(i))
            if elem:
                self.step18_fix_table_structure(elem)
                self.step19_move_tcredit_under_table(elem)
                self.step20_move_table_out_of_figure(elem)
                self.step21_move_figure_into_table(elem)
                self.step22_change_Figure_to_Caption(elem)
                self.step23_delete_story_if_only_table(elem)
                self.step24_move_table_before_heading(elem)

        if not doc.Save(output_path, kSaveFull):
            raise Exception(f"❌ Failed to save: {self.pdfix.GetError()}")

        doc.Close()
        print(f"✅ Phase 2 complete. Saved to: {output_path}")


class footprint:
    def __init__(self, pdfix):
        self.pdfix = pdfix

    def step25_delete_story_if_only_lb1l(self, elem: PdsStructElement, parent: PdsStructElement = None):
        st = elem.GetStructTree()
        fresh_elem = st.GetStructElementFromObject(elem.GetObject())
        if not fresh_elem:
            return

        # Only process <Story> tags
        if fresh_elem.GetType(False) == "Story" and parent:
            child_elements = []
            for i in range(fresh_elem.GetNumChildren()):
                if fresh_elem.GetChildType(i) == kPdsStructChildElement:
                    obj = fresh_elem.GetChildObject(i)
                    child = st.GetStructElementFromObject(obj)
                    if child:
                        child_elements.append(child)

            # ✅ Check if Story has exactly 1 child, and that child is <lb1l>
            if len(child_elements) == 1 and child_elements[0].GetType(False) == "lb1l":
                print("🧩 <Story> has only <lb1l> — deleting <Story> and keeping <lb1l>")

                # Get both Story and lb1l as fresh references
                story_ref = fresh_elem
                lb1l_ref = child_elements[0]

                # Find Story in its parent, then move lb1l out and delete Story
                for i in range(parent.GetNumChildren()):
                    if parent.GetChildType(i) != kPdsStructChildElement:
                        continue

                    obj = parent.GetChildObject(i)
                    if obj.obj == story_ref.GetObject().obj:
                        # Move <lb1l> into parent's child list (next position)
                        story_ref.MoveChild(0, parent, i + 1)

                        # Remove Story
                        parent.RemoveChild(i)
                        print("✅ <lb1l> successfully moved outside <Story>")
                        return

        # ✅ Recurse through the structure
        for i in range(fresh_elem.GetNumChildren()):
            if fresh_elem.GetChildType(i) == kPdsStructChildElement:
                obj = fresh_elem.GetChildObject(i)
                child_elem = st.GetStructElementFromObject(obj)
                if child_elem:
                    self.step25_delete_story_if_only_lb1l(child_elem, fresh_elem)

    def step26_unwrap_lb1l_from_p(self, elem: PdsStructElement, parent: PdsStructElement = None):
        st = elem.GetStructTree()
        fresh = st.GetStructElementFromObject(elem.GetObject())
        if not fresh:
            return

        # Process only <P> tags
        if fresh.GetType(False) == "P" and parent:
            if fresh.GetNumChildren() > 0 and fresh.GetChildType(0) == kPdsStructChildElement:
                first_obj = fresh.GetChildObject(0)
                first_child = st.GetStructElementFromObject(first_obj)

                if first_child and first_child.GetType(False) == "lb1l":
                    print("🔍 Found <lb1l> inside <P> — moving it ABOVE <P>...")

                    fresh_p = st.GetStructElementFromObject(fresh.GetObject())
                    fresh_parent = st.GetStructElementFromObject(parent.GetObject())
                    lb1l_elem = st.GetStructElementFromObject(first_child.GetObject())

                    # Find <P> index inside its parent
                    p_index = None
                    for i in range(fresh_parent.GetNumChildren()):
                        if fresh_parent.GetChildObject(i).obj == fresh_p.GetObject().obj:
                            p_index = i
                            break

                    if p_index is not None:
                        # ✅ Move <lb1l> ABOVE <P> (index stays same → inserted before)
                        fresh_p.MoveChild(0, fresh_parent, p_index)
                        print("✅ <lb1l> moved ABOVE <P> successfully!")

        # Continue recursion
        for i in range(fresh.GetNumChildren()):
            if fresh.GetChildType(i) == kPdsStructChildElement:
                child = st.GetStructElementFromObject(fresh.GetChildObject(i))
                if child:
                    self.step26_unwrap_lb1l_from_p(child, fresh)

    def step27_remove_lb1l_if_only_figure(self, elem: PdsStructElement, parent: PdsStructElement = None):
        st = elem.GetStructTree()
        fresh = st.GetStructElementFromObject(elem.GetObject())
        if not fresh:
            return

        # Process only lb1l tags
        if fresh.GetType(False) == "lb1l" and parent:
            num_kids = fresh.GetNumChildren()
            figure_child = None

            # ✅ Check if exactly 1 child and it's <Figure>
            if num_kids == 1 and fresh.GetChildType(0) == kPdsStructChildElement:
                obj = fresh.GetChildObject(0)
                child = st.GetStructElementFromObject(obj)

                if child and child.GetType(False) == "Figure":
                    figure_child = child

            if figure_child:
                print("🗑️ Removing <lb1l> wrapper — moving <Figure> to parent...")

                # Refresh references before modification
                fresh_lb1l = st.GetStructElementFromObject(fresh.GetObject())
                fresh_parent = st.GetStructElementFromObject(parent.GetObject())
                fresh_figure = st.GetStructElementFromObject(figure_child.GetObject())

                # ✅ Find index of lb1l inside parent
                lb1l_index = None
                for i in range(fresh_parent.GetNumChildren()):
                    if fresh_parent.GetChildObject(i).obj == fresh_lb1l.GetObject().obj:
                        lb1l_index = i
                        break

                if lb1l_index is not None:
                    # ✅ Move <Figure> to same position where <lb1l> existed
                    fresh_lb1l.MoveChild(0, fresh_parent, lb1l_index)
                    # ✅ Remove <lb1l>
                    fresh_parent.RemoveChild(lb1l_index + 1)

                    print("✅ <lb1l> removed and <Figure> lifted to parent")

        # Continue recursion
        for i in range(fresh.GetNumChildren()):
            if fresh.GetChildType(i) == kPdsStructChildElement:
                child = st.GetStructElementFromObject(fresh.GetChildObject(i))
                if child:
                    self.step27_remove_lb1l_if_only_figure(child, fresh)

    def step28_rename_double_figure_to_caption(self, elem: PdsStructElement, parent: PdsStructElement = None):
        st = elem.GetStructTree()
        fresh = st.GetStructElementFromObject(elem.GetObject())
        if not fresh:
            return

        # ✅ Only rename __Figure__ when its parent is <Figure>
        if parent is not None:
            parent_type = parent.GetType(False)
            elem_type = fresh.GetType(False)

            if elem_type == "__Figure__" and parent_type == "Figure":
                print("✏️ Renaming <__Figure__> → <Caption> under <Figure>")

                fresh.SetType("Caption")
                print("✅ Renamed successfully")

        # Recursively continue
        for i in range(fresh.GetNumChildren()):
            if fresh.GetChildType(i) == kPdsStructChildElement:
                child = st.GetStructElementFromObject(fresh.GetChildObject(i))
                if child:
                    self.step28_rename_double_figure_to_caption(child, fresh)

    def step29_remove_p_inside_caption(self, elem: PdsStructElement):
        st = elem.GetStructTree()
        fresh = st.GetStructElementFromObject(elem.GetObject())
        if not fresh:
            return

        # ✅ Process only <Caption> elements
        if fresh.GetType(False) == "Caption":
            if fresh.GetNumChildren() == 1:
                if fresh.GetChildType(0) == kPdsStructChildElement:
                    child = st.GetStructElementFromObject(fresh.GetChildObject(0))

                    if child and child.GetType(False) == "P":
                        print("🗑️ Removing <P> under <Caption> and keeping its children...")

                        # Move all children of <P> into <Caption>
                        num_kids = child.GetNumChildren()
                        for _ in range(num_kids):
                            child.MoveChild(0, fresh, -1)

                        # Remove <P>
                        fresh.RemoveChild(0)
                        print("✅ <P> removed successfully")

        # 🔁 Continue recursion
        for i in range(fresh.GetNumChildren()):
            if fresh.GetChildType(i) == kPdsStructChildElement:
                child = st.GetStructElementFromObject(fresh.GetChildObject(i))
                if child:
                    self.step29_remove_p_inside_caption(child)

    def step30_wrap_tfoot_content(self, elem: PdsStructElement):
        st = elem.GetStructTree()
        fresh = st.GetStructElementFromObject(elem.GetObject())
        if not fresh:
            return

        # ✅ Process only TFoot elements
        if fresh.GetType(False) == "TFoot":
            print("🔍 Checking <TFoot> structure...")

            has_tr = any(
                fresh.GetChildType(i) == kPdsStructChildElement and
                st.GetStructElementFromObject(fresh.GetChildObject(i)).GetType(False) == "TR"
                for i in range(fresh.GetNumChildren())
            )

            # Skip if TR already present
            if not has_tr and fresh.GetNumChildren() > 0:
                print("🧩 Wrapping content inside <TFoot> into <TR><TD>...")

                # Step 1: Create <TR> and <TD>
                tr_elem = fresh.AddNewChild("TR", -1)
                tr_struct = st.GetStructElementFromObject(tr_elem.GetObject())
                td_elem = tr_struct.AddNewChild("TD", -1)
                td_struct = st.GetStructElementFromObject(td_elem.GetObject())

                # Step 2: Move all children under <TD>
                num_kids = fresh.GetNumChildren()
                for _ in range(num_kids - 1):  # TR is last, so skip it
                    fresh.MoveChild(0, td_struct, -1)

                print("✅ Successfully wrapped TFoot content into <TR><TD>")

        # 🔁 Recursively process children
        for i in range(fresh.GetNumChildren()):
            if fresh.GetChildType(i) == kPdsStructChildElement:
                child = st.GetStructElementFromObject(fresh.GetChildObject(i))
                if child:
                    self.step30_wrap_tfoot_content(child)

    def step31_delete_if_only_T_col_hd(self, elem: PdsStructElement, parent: PdsStructElement = None):
        st = elem.GetStructTree()
        fresh_elem = st.GetStructElementFromObject(elem.GetObject())
        if not fresh_elem:
            return

        # Only process <Story> tags
        if fresh_elem.GetType(False) == "TH" and parent:
            child_elements = []
            for i in range(fresh_elem.GetNumChildren()):
                if fresh_elem.GetChildType(i) == kPdsStructChildElement:
                    obj = fresh_elem.GetChildObject(i)
                    child = st.GetStructElementFromObject(obj)
                    if child:
                        child_elements.append(child)

            # ✅ Check if Story has exactly 1 child, and that child is <T_col_hd>
            if len(child_elements) == 1 and child_elements[0].GetType(False) == "T_col_hd":
                print("🧩 <Story> has only <T_col_hd> — deleting <Story> and keeping <T_col_hd>")

                # Get both Story and T_col_hd as fresh references
                story_ref = fresh_elem
                T_col_hd_ref = child_elements[0]

                # Find Story in its parent, then move T_col_hd out and delete Story
                for i in range(parent.GetNumChildren()):
                    if parent.GetChildType(i) != kPdsStructChildElement:
                        continue

                    obj = parent.GetChildObject(i)
                    if obj.obj == story_ref.GetObject().obj:
                        # Move <T_col_hd> into parent's child list (next position)
                        story_ref.MoveChild(0, parent, i + 1)

                        # Remove Story
                        parent.RemoveChild(i)
                        print("✅ <T_col_hd> successfully moved outside <Story>")
                        return

        # ✅ Recurse through the structure
        for i in range(fresh_elem.GetNumChildren()):
            if fresh_elem.GetChildType(i) == kPdsStructChildElement:
                obj = fresh_elem.GetChildObject(i)
                child_elem = st.GetStructElementFromObject(obj)
                if child_elem:
                    self.step31_delete_if_only_T_col_hd(child_elem, fresh_elem)

    def step32_delete_story_if_only_T_body(self, elem: PdsStructElement, parent: PdsStructElement = None):
        st = elem.GetStructTree()
        fresh_elem = st.GetStructElementFromObject(elem.GetObject())
        if not fresh_elem:
            return

        # Only process <Story> tags
        if fresh_elem.GetType(False) == "TD" and parent:
            child_elements = []
            for i in range(fresh_elem.GetNumChildren()):
                if fresh_elem.GetChildType(i) == kPdsStructChildElement:
                    obj = fresh_elem.GetChildObject(i)
                    child = st.GetStructElementFromObject(obj)
                    if child:
                        child_elements.append(child)

            # ✅ Check if Story has exactly 1 child, and that child is <T_body>
            if len(child_elements) == 1 and child_elements[0].GetType(False) == "T_body":
                print("🧩 <Story> has only <T_body> — deleting <Story> and keeping <T_body>")

                # Get both Story and T_body as fresh references
                story_ref = fresh_elem
                T_body_ref = child_elements[0]

                # Find Story in its parent, then move T_body out and delete Story
                for i in range(parent.GetNumChildren()):
                    if parent.GetChildType(i) != kPdsStructChildElement:
                        continue

                    obj = parent.GetChildObject(i)
                    if obj.obj == story_ref.GetObject().obj:
                        # Move <T_body> into parent's child list (next position)
                        story_ref.MoveChild(0, parent, i + 1)

                        # Remove Story
                        parent.RemoveChild(i)
                        print("✅ <T_body> successfully moved outside <Story>")
                        return

        # ✅ Recurse through the structure
        for i in range(fresh_elem.GetNumChildren()):
            if fresh_elem.GetChildType(i) == kPdsStructChildElement:
                obj = fresh_elem.GetChildObject(i)
                child_elem = st.GetStructElementFromObject(obj)
                if child_elem:
                    self.step32_delete_story_if_only_T_body(child_elem, fresh_elem)

    def step33_delete_sect_with_normalparagraphstyle(self, elem: PdsStructElement, parent: PdsStructElement = None):
        st = elem.GetStructTree()
        fresh = st.GetStructElementFromObject(elem.GetObject())
        if not fresh:
            return

        # ✅ Only process <Sect> that has a parent
        if fresh.GetType(False) == "Sect" and parent:

            # Collect REAL element children (ignore text/whitespace nodes)
            real_children = []
            for i in range(fresh.GetNumChildren()):
                if fresh.GetChildType(i) == kPdsStructChildElement:
                    obj = fresh.GetChildObject(i)
                    child = st.GetStructElementFromObject(obj)
                    if child:
                        real_children.append(child)

            # ✅ Check if it has **one real child** and that child is <NormalParagraphStyle>
            if len(real_children) == 1 and real_children[0].GetType(False) == "NormalParagraphStyle":
                print("🗑️ Deleting <Sect> that only wraps <NormalParagraphStyle>...")

                sect_index = None
                for i in range(parent.GetNumChildren()):
                    if parent.GetChildType(i) == kPdsStructChildElement:
                        obj = parent.GetChildObject(i)
                        if obj.obj == fresh.GetObject().obj:
                            sect_index = i
                            break

                if sect_index is not None:
                    parent.RemoveChild(sect_index)
                    print("✅ <Sect> + <NormalParagraphStyle> removed")
                    return

        # 🔁 Continue recursion
        for i in range(fresh.GetNumChildren()):
            if fresh.GetChildType(i) == kPdsStructChildElement:
                child = st.GetStructElementFromObject(fresh.GetChildObject(i))
                if child:
                    self.step33_delete_sect_with_normalparagraphstyle(child, fresh)

    def step34_delete_sect_with_normalparagraphstyle(self, elem: PdsStructElement, parent: PdsStructElement = None):
        st = elem.GetStructTree()
        fresh = st.GetStructElementFromObject(elem.GetObject())
        if not fresh:
            return

        # ✅ Only process <Sect> that has a parent
        if fresh.GetType(False) == "Sect" and parent:

            # Collect REAL element children (ignore text/whitespace nodes)
            real_children = []
            for i in range(fresh.GetNumChildren()):
                if fresh.GetChildType(i) == kPdsStructChildElement:
                    obj = fresh.GetChildObject(i)
                    child = st.GetStructElementFromObject(obj)
                    if child:
                        real_children.append(child)

            # ✅ Check if it has **one real child** and that child is <NormalParagraphStyle>
            if len(real_children) == 1 and real_children[0].GetType(False) == "NormalParagraphStyle":
                print("🗑️ Deleting <Sect> that only wraps <NormalParagraphStyle>...")

                sect_index = None
                for i in range(parent.GetNumChildren()):
                    if parent.GetChildType(i) == kPdsStructChildElement:
                        obj = parent.GetChildObject(i)
                        if obj.obj == fresh.GetObject().obj:
                            sect_index = i
                            break

                if sect_index is not None:
                    parent.RemoveChild(sect_index)
                    print("✅ <Sect> + <NormalParagraphStyle> removed")
                    return

        # 🔁 Continue recursion
        for i in range(fresh.GetNumChildren()):
            if fresh.GetChildType(i) == kPdsStructChildElement:
                child = st.GetStructElementFromObject(fresh.GetChildObject(i))
                if child:
                    self.step34_delete_sect_with_normalparagraphstyle(child, fresh)

    def step35_wrap_story_with_TR(self, elem: PdsStructElement):
        if elem.GetType(False) == "TFoot":
            contains_double_fig = any(
                elem.GetStructTree().GetStructElementFromObject(elem.GetChildObject(i)).GetType(False) == "Link"
                for i in range(elem.GetNumChildren())
                if elem.GetChildType(i) == kPdsStructChildElement
            )

            if contains_double_fig:
                print("🧩 Wrapping <TFoot> content into <TR>")
                num_children = elem.GetNumChildren()
                if num_children == 0:
                    return
                lbl_elem = elem.AddNewChild("TR", 0)
                for _ in range(num_children):
                    if elem.GetNumChildren() > 1:
                        elem.MoveChild(1, lbl_elem, -1)

        for i in range(elem.GetNumChildren()):
            if elem.GetChildType(i) == kPdsStructChildElement:
                self.step35_wrap_story_with_TR(elem.GetStructTree().GetStructElementFromObject(elem.GetChildObject(i)))

    def step36_wrap_story_with_TD(self, elem: PdsStructElement):
        if elem.GetType(False) == "TR":
            contains_double_fig = any(
                elem.GetStructTree().GetStructElementFromObject(elem.GetChildObject(i)).GetType(False) == "Link"
                for i in range(elem.GetNumChildren())
                if elem.GetChildType(i) == kPdsStructChildElement
            )

            if contains_double_fig:
                print("🧩 Wrapping <TFoot> content into <TD>")
                num_children = elem.GetNumChildren()
                if num_children == 0:
                    return
                lbl_elem = elem.AddNewChild("TD", 0)
                for _ in range(num_children):
                    if elem.GetNumChildren() > 1:
                        elem.MoveChild(1, lbl_elem, -1)

        for i in range(elem.GetNumChildren()):
            if elem.GetChildType(i) == kPdsStructChildElement:
                self.step36_wrap_story_with_TD(elem.GetStructTree().GetStructElementFromObject(elem.GetChildObject(i)))

    def step37_rename_double_T_body_to_TR(self, elem: PdsStructElement, parent: PdsStructElement = None):
        st = elem.GetStructTree()
        fresh = st.GetStructElementFromObject(elem.GetObject())
        if not fresh:
            return

        # ✅ Only rename __Figure__ when its parent is <Figure>
        if parent is not None:
            parent_type = parent.GetType(False)
            elem_type = fresh.GetType(False)

            if elem_type == "T_body" and parent_type == "TR":
                print("✏️ Renaming <__Figure__> → <Caption> under <Figure>")

                fresh.SetType("TD")
                print("✅ Renamed successfully")

        # Recursively continue
        for i in range(fresh.GetNumChildren()):
            if fresh.GetChildType(i) == kPdsStructChildElement:
                child = st.GetStructElementFromObject(fresh.GetChildObject(i))
                if child:
                    self.step37_rename_double_T_body_to_TR(child, fresh)

    def step38_rename_double_T_col_hd_to_TR(self, elem: PdsStructElement, parent: PdsStructElement = None):
        st = elem.GetStructTree()
        fresh = st.GetStructElementFromObject(elem.GetObject())
        if not fresh:
            return

        # ✅ Only rename __Figure__ when its parent is <Figure>
        if parent is not None:
            parent_type = parent.GetType(False)
            elem_type = fresh.GetType(False)

            if elem_type == "T_col_hd" and parent_type == "TR":
                print("✏️ Renaming <__Figure__> → <Caption> under <Figure>")

                fresh.SetType("TD")
                print("✅ Renamed successfully")

        # Recursively continue
        for i in range(fresh.GetNumChildren()):
            if fresh.GetChildType(i) == kPdsStructChildElement:
                child = st.GetStructElementFromObject(fresh.GetChildObject(i))
                if child:
                    self.step38_rename_double_T_col_hd_to_TR(child, fresh)

    def step39_rename_td_to_th_in_thead(self,elem: PdsStructElement, parent=None, grandparent=None):
        """Rename TD → TH ONLY if TD is child of TR AND TR is child of THead."""
        st = elem.GetStructTree()
        fresh = st.GetStructElementFromObject(elem.GetObject())
        if not fresh:
            return

        # ✅ Rename conditions:
        # 1. Current element is <TD>
        # 2. Parent element is <TR>
        # 3. Grandparent is <THead>
        if (fresh.GetType(False) == "TD" and
                parent and parent.GetType(False) == "TR" and
                grandparent and grandparent.GetType(False) == "THead"):

            print(f"🔁 Renaming <TD> → <TH> under <THead>/<TR>")

            # Change struct type without affecting MCIDs (PAC-safe)
            if not fresh.SetType("TH"):
                print("⚠️ Failed to change type")
            else:
                print("✅ Renamed successfully")

        # 🔁 Recursively walk the structure tree
        for i in range(fresh.GetNumChildren()):
            if fresh.GetChildType(i) == kPdsStructChildElement:
                child = st.GetStructElementFromObject(fresh.GetChildObject(i))
                if child:
                    self.step39_rename_td_to_th_in_thead(child, fresh, parent)


    def process_article_formula1(self, elem: PdsStructElement):
            st = elem.GetStructTree()
            elem = st.GetStructElementFromObject(elem.GetObject())
            if not elem:
                return

            if elem.GetType(False) == "ADA_Eq_num":
                elem.SetType('Formula')

                # for i in range(elem.GetNumChildren()):
                #     if elem.GetChildType(i) == kPdsStructChildElement:
                #         obj = elem.GetChildObject(i)
                #         child = st.GetStructElementFromObject(obj)
                #         if child and child.GetType(False) == "chapter":
                #             print("<Story> → <Sect>")
                #             child.SetType("Sect")

            for i in range(elem.GetNumChildren()):
                if elem.GetChildType(i) == kPdsStructChildElement:
                    self.process_article_formula1(st.GetStructElementFromObject(elem.GetChildObject(i)))

    def step40_refernce_ptag_below(self, elem, parent=None):
        st = elem.GetStructTree()
        elem = st.GetStructElementFromObject(elem.GetObject())
        if not elem:
            return

        # ----------- CHECK: H2 contains "Reference" -----------
        if elem.GetType(False) == "H2":
            text = elem.GetText(False) or ""
            if "reference" in text.lower().strip():

                # Find next sibling under same parent
                if parent:
                    for i in range(parent.GetNumChildren()):
                        cobj = parent.GetChildObject(i)
                        child = st.GetStructElementFromObject(cobj)
                        if not child:
                            continue

                        # find the H2 in the parent
                        if child.GetObject().obj == elem.GetObject().obj:
                            # next sibling
                            next_index = i + 1
                            if next_index < parent.GetNumChildren():

                                nobj = parent.GetChildObject(next_index)
                                next_elem = st.GetStructElementFromObject(nobj)

                                if next_elem and next_elem.GetType(False) == "L":
                                    print("📌 H2(Reference) found followed by <L> — fixing...")

                                    # ---- Create new <P> under parent ----
                                    new_p = parent.AddNewChild("P", next_index)
                                    new_p_elem = st.GetStructElementFromObject(new_p.GetObject())

                                    # ---- Move <L> under new <P> ----
                                    parent.MoveChild(next_index + 1, new_p_elem, -1)

                                    print("✅ Created <P> and moved <L> inside it")
                            break

        # ---------- RECURSE ----------
        for i in range(elem.GetNumChildren()):
            if elem.GetChildType(i) == kPdsStructChildElement:
                cobj = elem.GetChildObject(i)
                ch = st.GetStructElementFromObject(cobj)
                if ch:
                    self.step40_refernce_ptag_below(ch, elem)

    def modify_pdf_tags(self, input_path, output_path):
        doc = self.pdfix.OpenDoc(input_path, "")
        if not doc:
            raise Exception("❌ Failed to open PDF")

        st = doc.GetStructTree()
        print("🚀 Starting Phase 2 transformations...")

        for i in range(st.GetNumChildren()):
            elem = st.GetStructElementFromObject(st.GetChildObject(i))
            if elem:
                self.step25_delete_story_if_only_lb1l(elem)
                self.step26_unwrap_lb1l_from_p(elem)
                self.step27_remove_lb1l_if_only_figure(elem)
                self.step28_rename_double_figure_to_caption(elem)
                # self.step29_remove_p_inside_caption(elem)
                # self.step30_wrap_tfoot_content(elem)
                self.step31_delete_if_only_T_col_hd(elem)
                self.step32_delete_story_if_only_T_body(elem)
                self.step33_delete_sect_with_normalparagraphstyle(elem)
                self.step34_delete_sect_with_normalparagraphstyle(elem)
                self.step37_rename_double_T_body_to_TR(elem)
                self.step38_rename_double_T_col_hd_to_TR(elem)
                # self.step35_wrap_story_with_TR(elem)
                # self.step36_wrap_story_with_TD(elem)
                self.step39_rename_td_to_th_in_thead(elem)
                # self.process_article_formula1(elem)
                self.step40_refernce_ptag_below(elem)

        if not doc.Save(output_path, kSaveFull):
            raise Exception(f"❌ Failed to save: {self.pdfix.GetError()}")

        doc.Close()
        print(f"✅ Phase 2 complete. Saved to: {output_path}")

class Table_delete:
    """Handles steps 1–13 of the PDF tag transformation process."""

    def __init__(self, pdfix):
        self.pdfix = pdfix
        if not pdfix:
            raise Exception("❌ Pdfix initialization failed")

    # -------------------- Helper --------------------
    def jsonToRawData(self, json_dict):
        json_str = json.dumps(json_dict)
        json_data = bytearray(json_str.encode("utf-8"))
        json_data_size = len(json_str)
        json_data_raw = (ctypes.c_ubyte * json_data_size).from_buffer(json_data)
        return json_data_raw, json_data_size

    # -------------------- Step 1 --------------------
    def test3_process_article_story(self, elem: PdsStructElement):
        st = elem.GetStructTree()
        elem = st.GetStructElementFromObject(elem.GetObject())
        if not elem:
            return

        if elem.GetType(False) == "TD":
            for i in range(elem.GetNumChildren()):
                if elem.GetChildType(i) == kPdsStructChildElement:
                    obj = elem.GetChildObject(i)
                    child = st.GetStructElementFromObject(obj)
                    if child and child.GetType(False) == "T_body":
                        print("🧩 <T_body> → <Test3>")
                        child.SetType("Test3")

        for i in range(elem.GetNumChildren()):
            if elem.GetChildType(i) == kPdsStructChildElement:
                self.test3_process_article_story(st.GetStructElementFromObject(elem.GetChildObject(i)))


    def test4_process_article_story(self, elem: PdsStructElement):
        st = elem.GetStructTree()
        elem = st.GetStructElementFromObject(elem.GetObject())
        if not elem:
            return

        if elem.GetType(False) == "TH":
            for i in range(elem.GetNumChildren()):
                if elem.GetChildType(i) == kPdsStructChildElement:
                    obj = elem.GetChildObject(i)
                    child = st.GetStructElementFromObject(obj)
                    if child and child.GetType(False) == "T_col_hd":
                        print("🧩 <T_col_hd> → <Test4>")
                        child.SetType("Test4")

        for i in range(elem.GetNumChildren()):
            if elem.GetChildType(i) == kPdsStructChildElement:
                self.test4_process_article_story(st.GetStructElementFromObject(elem.GetChildObject(i)))


    # -------------------- Step 3 --------------------
    def delete_tags_in_pdf(self, doc, tag_name):
        json_dict = {
            "commands": [
                {
                    "name": "delete_tags",
                    "params": [
                        {"name": "tag_names", "value": tag_name},
                        {"name": "exclude_tag_names", "value": "false"},
                        {"name": "skip_tag_names", "value": ""},
                        {"name": "flags", "value": 255},
                        {"name": "tag_content", "value": "move"},
                    ],
                }
            ]
        }

        json_data, json_size = self.jsonToRawData(json_dict)
        memStm = self.pdfix.CreateMemStream()
        memStm.Write(0, json_data, json_size)
        command = doc.GetCommand()
        command.LoadParamsFromStream(memStm, kDataFormatJson)
        memStm.Destroy()

        print(f"🗑️ Removing <{tag_name}>...")
        if not command.Run():
            raise Exception("❌ Failed to delete tags: " + self.pdfix.GetError())



    # -------------------- Run All Steps --------------------
    def modify_pdf_tags(self, input_path, output_path):
        doc = self.pdfix.OpenDoc(input_path, "")
        if not doc:
            raise Exception("❌ Failed to open PDF")

        st = doc.GetStructTree()
        if not st:
            raise Exception("❌ No structure tree found")

        print("🚀 Starting Phase 1 transformations...")

        for i in range(st.GetNumChildren()):
            elem = st.GetStructElementFromObject(st.GetChildObject(i))
            if elem:
                self.test3_process_article_story(elem)
                self.test4_process_article_story(elem)
                # self.move_number_into_figure(elem)


        self.delete_tags_in_pdf(doc, "Test3")
        self.delete_tags_in_pdf(doc, "Test4")
        # self.delete_tags_in_pdf(doc, "Eq_num")

        if not doc.Save(output_path, kSaveFull):
            raise Exception(f"❌ Failed to save PDF: {self.pdfix.GetError()}")

        doc.Close()
        print(f"✅ Phase 1 complete. Saved to: {output_path}")

class PdfAltTextSetter:
    """Sets Alt text 'display equation' for all <Formula> tags in a PDF."""

    def __init__(self, pdfix):
        self.pdfix = pdfix
        if not pdfix:
            raise Exception("❌ Pdfix initialization failed")

    def set_alt_for_formula(self, elem: PdsStructElement):
        """Recursively finds all <Formula> tags and sets Alt text."""
        st = elem.GetStructTree()
        fresh_elem = st.GetStructElementFromObject(elem.GetObject())
        if not fresh_elem:
            return

        tag_name = fresh_elem.GetType(False)

        # ✅ If it's a <Formula>, set Alt text
        if tag_name == "Formula":
            success = fresh_elem.SetActualText("Display Equation")
            if success:
                print("✅ Set Alt text 'display equation' for <Formula>")
            else:
                print("⚠️ Failed to set Alt text for <Formula>")

        # 🔁 Recurse through all children
        for i in range(fresh_elem.GetNumChildren()):
            if fresh_elem.GetChildType(i) == kPdsStructChildElement:
                child_obj = fresh_elem.GetChildObject(i)
                child_elem = st.GetStructElementFromObject(child_obj)
                if child_elem:
                    self.set_alt_for_formula(child_elem)

    def modify_pdf(self, input_path, output_path):
        """Main entry point: open, process, and save PDF."""
        doc = self.pdfix.OpenDoc(input_path, "")
        if not doc:
            raise Exception("❌ Failed to open PDF")

        st = doc.GetStructTree()
        if not st:
            raise Exception("❌ No structure tree found in PDF")

        print("🚀 Setting Alt text 'display equation' for all <Formula> tags...")

        # Traverse all structure elements
        for i in range(st.GetNumChildren()):
            obj = st.GetChildObject(i)
            elem = st.GetStructElementFromObject(obj)
            if elem:
                self.set_alt_for_formula(elem)

        # ✅ Save updated PDF
        if not doc.Save(output_path, kSaveFull):
            raise Exception(f"❌ Failed to save PDF: {self.pdfix.GetError()}")

        doc.Close()
        print(f"✅ Alt text added successfully. Saved to: {output_path}")



class Figure_inlineequation:
    """Handles steps 1–13 of the PDF tag transformation process."""

    def __init__(self, pdfix):
        self.pdfix = pdfix
        if not pdfix:
            raise Exception("❌ Pdfix initialization failed")

    def rename_figure_without_caption(self,elem: PdsStructElement):
        st = elem.GetStructTree()
        fresh = st.GetStructElementFromObject(elem.GetObject())
        if not fresh:
            return

        # Check if this tag is <Figure>
        if fresh.GetType(False) == "Figure":
            has_caption = False

            # Scan its children to see if Caption exists
            for i in range(fresh.GetNumChildren()):
                if fresh.GetChildType(i) == kPdsStructChildElement:
                    child = st.GetStructElementFromObject(fresh.GetChildObject(i))
                    if not child:
                        continue

                    if child.GetType(False) == "Caption":
                        has_caption = True
                        break

            # Rename only if NOT contains caption
            if not has_caption:
                print("🔄 Changing <Figure> → <Test10>")
                fresh.SetType("Test10")  # rename tag, safe & PAC-compatible

        # Recursion
        for i in range(fresh.GetNumChildren()):
            if fresh.GetChildType(i) == kPdsStructChildElement:
                child = st.GetStructElementFromObject(fresh.GetChildObject(i))
                if child:
                    self.rename_figure_without_caption(child)


    def set_alt_for_formula(self, elem: PdsStructElement):
        """Recursively finds all <Formula> tags and sets Alt text."""
        st = elem.GetStructTree()
        fresh_elem = st.GetStructElementFromObject(elem.GetObject())
        if not fresh_elem:
            return

        tag_name = fresh_elem.GetType(False)

        # ✅ If it's a <Formula>, set Alt text
        if tag_name == "Test10":
            success = fresh_elem.SetActualText("Inline Equation")
            if success:
                print("✅ Set Alt text 'display equation' for <Formula>")
            else:
                print("⚠️ Failed to set Alt text for <Formula>")

        # 🔁 Recurse through all children
        for i in range(fresh_elem.GetNumChildren()):
            if fresh_elem.GetChildType(i) == kPdsStructChildElement:
                child_obj = fresh_elem.GetChildObject(i)
                child_elem = st.GetStructElementFromObject(child_obj)
                if child_elem:
                    self.set_alt_for_formula(child_elem)


    def test4_process_article_story(self, elem: PdsStructElement):
        st = elem.GetStructTree()
        elem = st.GetStructElementFromObject(elem.GetObject())
        if not elem:
            return

        if elem.GetType(False) == "P":
            for i in range(elem.GetNumChildren()):
                if elem.GetChildType(i) == kPdsStructChildElement:
                    obj = elem.GetChildObject(i)
                    child = st.GetStructElementFromObject(obj)
                    if child and child.GetType(False) == "Test10":
                        print("🧩 <T_col_hd> → <Test4>")
                        child.SetType("Formula")

        for i in range(elem.GetNumChildren()):
            if elem.GetChildType(i) == kPdsStructChildElement:
                self.test4_process_article_story(st.GetStructElementFromObject(elem.GetChildObject(i)))

    # -------------------- Run All Steps --------------------
    def modify_pdf_tags(self, input_path, output_path):
        doc = self.pdfix.OpenDoc(input_path, "")
        if not doc:
            raise Exception("❌ Failed to open PDF")

        st = doc.GetStructTree()
        if not st:
            raise Exception("❌ No structure tree found")

        print("🚀 Starting Phase 1 transformations...")

        for i in range(st.GetNumChildren()):
            elem = st.GetStructElementFromObject(st.GetChildObject(i))
            if elem:
                self.rename_figure_without_caption(elem)
                self.set_alt_for_formula(elem)
                self.test4_process_article_story(elem)


        if not doc.Save(output_path, kSaveFull):
            raise Exception(f"❌ Failed to save PDF: {self.pdfix.GetError()}")

        doc.Close()
        print(f"✅ Phase 1 complete. Saved to: {output_path}")



class formula_inside_figure_delete:
    """Handles steps 1–13 of the PDF tag transformation process."""

    def __init__(self, pdfix):
        self.pdfix = pdfix
        if not pdfix:
            raise Exception("❌ Pdfix initialization failed")

    # -------------------- Helper --------------------
    def jsonToRawData(self, json_dict):
        json_str = json.dumps(json_dict)
        json_data = bytearray(json_str.encode("utf-8"))
        json_data_size = len(json_str)
        json_data_raw = (ctypes.c_ubyte * json_data_size).from_buffer(json_data)
        return json_data_raw, json_data_size

    # -------------------- Step 1 --------------------
    def test3_process_article_story(self, elem: PdsStructElement):
        st = elem.GetStructTree()
        elem = st.GetStructElementFromObject(elem.GetObject())
        if not elem:
            return

        if elem.GetType(False) == "Formula":
            for i in range(elem.GetNumChildren()):
                if elem.GetChildType(i) == kPdsStructChildElement:
                    obj = elem.GetChildObject(i)
                    child = st.GetStructElementFromObject(obj)
                    if child and child.GetType(False) == "Figure":
                        print("🧩 <T_body> → <Test3>")
                        child.SetType("Test12")

        for i in range(elem.GetNumChildren()):
            if elem.GetChildType(i) == kPdsStructChildElement:
                self.test3_process_article_story(st.GetStructElementFromObject(elem.GetChildObject(i)))


    def test4_process_article_story(self, elem: PdsStructElement):
        st = elem.GetStructTree()
        elem = st.GetStructElementFromObject(elem.GetObject())
        if not elem:
            return

        if elem.GetType(False) == "P":
            for i in range(elem.GetNumChildren()):
                if elem.GetChildType(i) == kPdsStructChildElement:
                    obj = elem.GetChildObject(i)
                    child = st.GetStructElementFromObject(obj)
                    if child and child.GetType(False) == "Test3":
                        print("🧩 <T_col_hd> → <Test4>")
                        child.SetType("Formula")

        for i in range(elem.GetNumChildren()):
            if elem.GetChildType(i) == kPdsStructChildElement:
                self.test4_process_article_story(st.GetStructElementFromObject(elem.GetChildObject(i)))



    def set_alt_for_formula(self, elem: PdsStructElement):
        """Recursively finds all <Formula> tags and sets Alt text."""
        st = elem.GetStructTree()
        fresh_elem = st.GetStructElementFromObject(elem.GetObject())
        if not fresh_elem:
            return

        tag_name = fresh_elem.GetType(False)

        # ✅ If it's a <Formula>, set Alt text
        if tag_name == "Test3":
            success = fresh_elem.SetActualText("Inline Equation")
            if success:
                print("✅ Set Alt text 'display equation' for <Formula>")
            else:
                print("⚠️ Failed to set Alt text for <Formula>")

        # 🔁 Recurse through all children
        for i in range(fresh_elem.GetNumChildren()):
            if fresh_elem.GetChildType(i) == kPdsStructChildElement:
                child_obj = fresh_elem.GetChildObject(i)
                child_elem = st.GetStructElementFromObject(child_obj)
                if child_elem:
                    self.set_alt_for_formula(child_elem)



    # -------------------- Step 3 --------------------
    def delete_tags_in_pdf(self, doc, tag_name):
        json_dict = {
            "commands": [
                {
                    "name": "delete_tags",
                    "params": [
                        {"name": "tag_names", "value": tag_name},
                        {"name": "exclude_tag_names", "value": "false"},
                        {"name": "skip_tag_names", "value": ""},
                        {"name": "flags", "value": 255},
                        {"name": "tag_content", "value": "move"},
                    ],
                }
            ]
        }

        json_data, json_size = self.jsonToRawData(json_dict)
        memStm = self.pdfix.CreateMemStream()
        memStm.Write(0, json_data, json_size)
        command = doc.GetCommand()
        command.LoadParamsFromStream(memStm, kDataFormatJson)
        memStm.Destroy()

        print(f"🗑️ Removing <{tag_name}>...")
        if not command.Run():
            raise Exception("❌ Failed to delete tags: " + self.pdfix.GetError())


    # -------------------- Run All Steps --------------------
    def modify_pdf_tags(self, input_path, output_path):
        doc = self.pdfix.OpenDoc(input_path, "")
        if not doc:
            raise Exception("❌ Failed to open PDF")

        st = doc.GetStructTree()
        if not st:
            raise Exception("❌ No structure tree found")

        print("🚀 Starting Phase 1 transformations...")

        for i in range(st.GetNumChildren()):
            elem = st.GetStructElementFromObject(st.GetChildObject(i))
            if elem:
                self.test3_process_article_story(elem)



        self.delete_tags_in_pdf(doc, "Test10")
  

        if not doc.Save(output_path, kSaveFull):
            raise Exception(f"❌ Failed to save PDF: {self.pdfix.GetError()}")

        doc.Close()
        print(f"✅ Phase 1 complete. Saved to: {output_path}")



