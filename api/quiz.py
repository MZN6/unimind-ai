import os
import json
import re
from http.server import BaseHTTPRequestHandler
import anthropic


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors()
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))

            pdf_text   = body.get("pdf_text", "").strip()
            num_q      = int(body.get("num_questions", 8))
            difficulty = body.get("difficulty", "medium")

            if not pdf_text:
                return self._error(400, "pdf_text مطلوب")

            num_q = max(3, min(num_q, 15))
            diff_label = {"easy": "سهلة", "medium": "متوسطة الصعوبة", "hard": "صعبة"}.get(difficulty, "متوسطة")

            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                return self._error(500, "مفتاح API غير مُعيَّن على الخادم")

            client = anthropic.Anthropic(api_key=api_key)

            system = """أنت مساعد جامعي متخصص في إنشاء اختبارات أكاديمية.
أرجع فقط JSON array بدون أي نص إضافي أو markdown، بالصيغة التالية تماماً:
[
  {
    "q": "نص السؤال",
    "options": ["أ) خيار1", "ب) خيار2", "ج) خيار3", "د) خيار4"],
    "answer": 0,
    "explain": "شرح مختصر للإجابة الصحيحة"
  }
]
حيث "answer" هو index الإجابة الصحيحة (0-3)."""

            user = f"""من المحاضرة التالية، أنشئ {num_q} أسئلة اختيار متعدد {diff_label}.
أسئلة واضحة ومرتبطة بمحتوى المحاضرة فقط.

المحاضرة:
{pdf_text[:11000]}"""

            response = client.messages.create(
              model="claude-3-5-sonnet-20241022",
                max_tokens=2500,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            raw = response.content[0].text

            # Extract JSON array robustly
            match = re.search(r"\[.*\]", raw, re.DOTALL)
            if not match:
                return self._error(500, "لم يتمكن النموذج من توليد اختبار صالح، حاول مجدداً.")
            quiz = json.loads(match.group())

            self.send_response(200)
            self._set_cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"quiz": quiz}, ensure_ascii=False).encode())

        except Exception as e:
            self._error(500, str(e))

    def _set_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _error(self, code: int, msg: str):
        self.send_response(code)
        self._set_cors()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps({"error": msg}, ensure_ascii=False).encode())
