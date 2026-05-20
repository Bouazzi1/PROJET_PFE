import os
import tempfile

from PIL import Image


class OCRService:
    def __init__(self):
        self._easy_ocr = None

    def _get_easy_ocr(self):
        if self._easy_ocr is None:
            try:
                import easyocr
                self._easy_ocr = easyocr.Reader(["en"], gpu=False, verbose=False)
                print("[OCRService] EasyOCR loaded OK")
            except Exception as e:
                print(f"[OCRService] EasyOCR unavailable: {e}")
                self._easy_ocr = "unavailable"
        return None if self._easy_ocr == "unavailable" else self._easy_ocr

    async def extract_passport(
        self, image_bytes: bytes, client_id: str | None = None
    ) -> dict:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(image_bytes)
            temp_path = f.name

        try:
            raw_text = self._ocr_text(temp_path)
            mrz_data = self._extract_mrz(temp_path)

            passport_data = {
                "passport_number": mrz_data.get("number"),
                "surname":         mrz_data.get("surname"),
                "given_names":     mrz_data.get("names"),
                "nationality":     mrz_data.get("nationality"),
                "date_of_birth":   mrz_data.get("date_of_birth"),
                "sex":             mrz_data.get("sex"),
                "date_of_expiry":  mrz_data.get("expiration_date"),
                "mrz_line1":       mrz_data.get("mrz1"),
                "mrz_line2":       mrz_data.get("mrz2"),
                "raw_ocr_text":    raw_text,
            }

            if not passport_data["passport_number"]:
                passport_data["passport_number"] = self._find_passport_number(
                    raw_text.splitlines()
                )
        finally:
            try:
                os.unlink(temp_path)
            except Exception:
                pass

        return {
            "passport_data": passport_data,
            "raw_text":      raw_text,
            "client_id":     client_id,
        }

    def _ocr_text(self, image_path: str) -> str:
        # 1. EasyOCR (primary — deep learning, Docker CPU compatible)
        reader = self._get_easy_ocr()
        if reader:
            try:
                results = reader.readtext(image_path, detail=1)
                texts = [text for (_, text, conf) in results if conf > 0.5]
                if texts:
                    return "\n".join(texts)
            except Exception as e:
                print(f"[OCRService] EasyOCR predict failed: {e}")

        # 2. pytesseract (fallback)
        try:
            import pytesseract
            img = Image.open(image_path)
            return pytesseract.image_to_string(img, lang="eng")
        except Exception as e:
            print(f"[OCRService] pytesseract failed: {e}")
            return ""

    def _extract_mrz(self, image_path: str) -> dict:
        try:
            from passporteye import read_mrz
            mrz = read_mrz(image_path)
            if mrz is None:
                return {}
            mrz_data = mrz.to_dict()
            return {
                "number":          mrz_data.get("number", "").replace("<", "").replace("K", "").strip(),
                "surname":         self._clean_mrz_field(mrz_data.get("surname", "")),
                "names":           self._clean_mrz_field(mrz_data.get("names", "")),
                "nationality":     mrz_data.get("nationality", "").replace("<", "").replace("K", "").strip(),
                "date_of_birth":   self._format_mrz_date(mrz_data.get("date_of_birth", "")),
                "sex":             mrz_data.get("sex", "").strip(),
                "expiration_date": self._format_mrz_date(mrz_data.get("expiration_date", "")),
                "mrz1":            mrz_data.get("mrz1", ""),
                "mrz2":            mrz_data.get("mrz2", ""),
            }
        except Exception as e:
            print(f"[OCRService] passporteye failed: {e}")
            return {}

    def _clean_mrz_field(self, value: str) -> str:
        import re
        cleaned = value.replace("<", " ").replace("K", " ")
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def _format_mrz_date(self, date_str: str) -> str | None:
        if not date_str or len(date_str) != 6:
            return None
        yy, mm, dd = date_str[:2], date_str[2:4], date_str[4:6]
        prefix = "19" if int(yy) > 50 else "20"
        return f"{prefix}{yy}-{mm}-{dd}"

    def _find_passport_number(self, texts: list[str]) -> str | None:
        import re
        for text in texts:
            match = re.search(r'[A-Z]{1,2}\d{6,8}', text)
            if match:
                return match.group()
        return None


ocr_service = OCRService()
