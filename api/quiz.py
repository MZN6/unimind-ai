import os
import json
import re
from http.server import BaseHTTPRequestHandler
from openai import OpenAI


class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors()
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))

            pdf_text = body.get("pdf_text", "").strip()
            num_q = int(body.get("num_questions", 8))
            difficulty = body.get("difficulty", "medium")

            if not pdf_text:
                return self._error(400, "pdf_text مطلوب")

            num_q = max(3, min(num_q, 15))

            diff_label = {
                "easy": "سهلة",
                "medium": "متوسطة الصعوبة",
                "hard": "صعبة"
            }.get(difficulty, "متوسطة")

            api_key = os.environ.get("OPENAI_API_KEY")

            if not api_key:
                return self._error(500, "OPENAI_API_KEY غير موجود")

            client = OpenAI(api_key=api_key)

            system = """أنت مساعد جامعي متخصص في إنشاء اختبارات أكاديمية.

أرجع فقط JSON array بدون أي نص إضافي أو markdown، بالصيغة التالية:

[
  {
    "q": "نص السؤال",
    "options": ["أ) خيار1", "ب) خيار2", "ج) خيار3", "د) خيار4"],
    "answer": 0,
    "explain": "شرح مختصر للإجابة الصحيحة"
  }
]

حيث answer هو رقم الإجابة الصحيحة من 0 إلى 3.
"""

            user = f"""
من المحاضرة التالية، أنشئ {num_q} أسئلة اختيار متعدد {diff_label}.

المحاضرة:
{pdf_text[:11000]}
"""

            response = client.responses.create(
                model="gpt-4o-mini",
                input=system + "\n\n" + user,
            )

            raw = response.output_text

            match = re.search(r"\[.*\]", raw, re.DOTALL)

            if not match:
                return self._error(500, "فشل إنشاء الاختبار")

            quiz = json.loads(match.group())

            self.send_response(200)
            self._set_cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()

            self.wfile.write(
                json.dumps(
                    {"quiz": quiz},
                    ensure_ascii=False
                ).encode()
            )

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

        self.wfile.write(
            json.dumps(
                {"error": msg},
                ensure_ascii=False
            ).encode()
        )
