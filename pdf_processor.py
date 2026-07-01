import fitz, re, logging, shutil
logger = logging.getLogger(__name__)

class PDFProcessor:
    def extract_text(self, pdf_path):
        try:
            doc = fitz.open(pdf_path)
            t = "".join(p.get_text() for p in doc)
            doc.close(); return t
        except Exception as e: logger.error(e); return ""

    def replace_text(self, pdf_path, find_text, replace_text, output_path):
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                for r in page.search_for(find_text): page.add_redact_annot(r, fill=(1,1,1))
                page.apply_redactions()
                for r in page.search_for(find_text): page.insert_text(r.tl, replace_text, fontsize=11)
            doc.save(output_path); doc.close(); return True
        except Exception as e: logger.error(e); return False

    def increase_prices(self, pdf_path, percent, output_path):
        try:
            doc = fitz.open(pdf_path); out = fitz.open()
            for page in doc:
                nums = re.findall(r'\b\d+(?:[.,]\d+)?\b', page.get_text())
                nd = fitz.open(pdf_path); np2 = nd[page.number]
                for ns in set(nums):
                    try:
                        v = float(ns.replace(',','.')); nv = v*(1+percent/100)
                        ns2 = f"{nv:.2f}".replace('.',',') if ',' in ns else f"{nv:.2f}"
                        for r in np2.search_for(ns): np2.add_redact_annot(r, fill=(1,1,1))
                        np2.apply_redactions()
                        for r in np2.search_for(ns): np2.insert_text(r.tl, ns2, fontsize=11)
                    except: continue
                out.insert_pdf(nd, from_page=page.number, to_page=page.number); nd.close()
            out.save(output_path); out.close(); doc.close(); return True
        except Exception as e: logger.error(e); return False

    def apply_actions(self, pdf_path, actions, output_path):
        current = pdf_path; tmp = output_path+".tmp.pdf"
        try:
            for i, a in enumerate(actions):
                out = tmp if i < len(actions)-1 else output_path
                t = a.get("type","")
                if t == "replace_text": self.replace_text(current, a.get("find",""), a.get("replace",""), out)
                elif t == "increase_prices": self.increase_prices(current, float(a.get("percent",10)), out)
                elif t == "decrease_prices": self.increase_prices(current, -float(a.get("percent",10)), out)
                elif t == "add_text": self._add_text(current, a.get("text",""), out)
                else: shutil.copy(current, out)
                current = out
            return True
        except Exception as e: logger.error(e); shutil.copy(pdf_path, output_path); return False

    def _add_text(self, pdf_path, text, output_path):
        try:
            doc = fitz.open(pdf_path); doc[0].insert_text((72,72), text, fontsize=12)
            doc.save(output_path); doc.close(); return True
        except Exception as e: logger.error(e); return False
