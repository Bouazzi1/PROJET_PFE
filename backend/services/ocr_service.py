import io
import tempfile

from PIL import Image


class OCRService:
    def __init__(self):
        self._paddle_ocr = None
        self._passport_eye_available = False

    def _get_paddle_ocr(self):
        if self._paddle_ocr is None:
            from paddleocr import PaddleOCR
            self._paddle_ocr = PaddleOCR(
                use_angle_cls=True,
                lang="en",
                use_gpu=False,
                show_log=False,
            )
        return self._paddle_ocr

    async def extract_passport(
        self, image_bytes: bytes, client_id: str | None = None
    ) -> dict:
        # Save to temp file for processing
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(image_bytes)
            temp_path = f.name

        # PaddleOCR extraction
        ocr = self._get_paddle_ocr()
        result = ocr.ocr(temp_path, cls=True)

        ocr_texts = []
        if result and result[0]:
            for line in result[0]:
                text = line[1][0]
                confidence = line[1][1]
                if confidence > 0.5:
                    ocr_texts.append(text)

        raw_text = "\n".join(ocr_texts)

        # MRZ extraction via passporteye
        mrz_data = self._extract_mrz(temp_path)

        # Merge results
        passport_data = {
            "passport_number": mrz_data.get("number"),
            "surname": mrz_data.get("surname"),
            "given_names": mrz_data.get("names"),
            "nationality": mrz_data.get("nationality"),
            "date_of_birth": mrz_data.get("date_of_birth"),
            "sex": mrz_data.get("sex"),
            "date_of_expiry": mrz_data.get("expiration_date"),
            "mrz_line1": mrz_data.get("mrz1"),
            "mrz_line2": mrz_data.get("mrz2"),
            "raw_ocr_text": raw_text,
        }

        # Try to fill missing fields from OCR text
        if not passport_data["passport_number"]:
            passport_data["passport_number"] = self._find_passport_number(ocr_texts)

        return {
            "passport_data": passport_data,
            "raw_text": raw_text,
            "client_id": client_id,
        }

    def _extract_mrz(self, image_path: str) -> dict:
        try:
            from passporteye import read_mrz
            mrz = read_mrz(image_path)
            if mrz is None:
                return {}
            mrz_data = mrz.to_dict()
            return {
                "number": mrz_data.get("number", "").replace("<", ""),
                "surname": mrz_data.get("surname", "").replace("<", " ").strip(),
                "names": mrz_data.get("names", "").replace("<", " ").strip(),
                "nationality": mrz_data.get("nationality", ""),
                "date_of_birth": self._format_mrz_date(mrz_data.get("date_of_birth", "")),
                "sex": mrz_data.get("sex", ""),
                "expiration_date": self._format_mrz_date(mrz_data.get("expiration_date", "")),
                "mrz1": mrz_data.get("mrz1", ""),
                "mrz2": mrz_data.get("mrz2", ""),
            }
        except Exception:
            return {}

    def _format_mrz_date(self, date_str: str) -> str | None:
        if not date_str or len(date_str) != 6:
            return None
        yy, mm, dd = date_str[:2], date_str[2:4], date_str[4:6]
        year = int(yy)
        prefix = "19" if year > 50 else "20"
        return f"{prefix}{yy}-{mm}-{dd}"

    def _find_passport_number(self, texts: list[str]) -> str | None:
        import re
        for text in texts:
            match = re.search(r'[A-Z]{1,2}\d{6,8}', text)
            if match:
                return match.group()
        return None


ocr_service = OCRService()
