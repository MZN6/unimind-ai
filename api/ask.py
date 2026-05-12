import os
import json
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

            pdf_text = body.get("pdf_text", "").strip()
            question = body.get("question", "").strip()

            if not pdf_text:
                return self._error(400, "pdf_text مطلوب")
            if not question:
                return self._error(400, "question مطلوب")

            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                return self._error(500, "مفتاح API غير مُعيَّن على الخادم")

            client = anthropic.Anthropic(api_key=api_key)

            system = """أنت مساعد جامعي عربي متخصص ومحترف.
قواعدك:
- أجب فقط بناءً على محتوى ملف المحاضرة المعطى لك.
- اشرح بأسلوب بسيط وواضح مناسب للطلاب الجامعيين.
- إذا لم تجد الإجابة في المحاضرة، قل: "هذه المعلومة غير موجودة في الملف."
- نسّق إجابتك بشكل جيد: استخدم العناوين والنقاط عند الضرورة.
- لا تخترع معلومات."""

            user = f"""محتوى المحاضرة:
{pdf_text[:14000]}

سؤال الطالب:
{question}"""

            response = client.messages.create(
               model="claude-3-5-sonnet-20241022",
                max_tokens=1500,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            answer = response.content[0].text

            self.send_response(200)
            self._set_cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"answer": answer}, ensure_ascii=False).encode())

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
