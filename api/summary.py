import os
import json
from http.server import BaseHTTPRequestHandler
import anthropic


SUMMARY_PROMPTS = {
    "quick":    "لخّص هذه المحاضرة في ما لا يزيد عن 500 كلمة. كن دقيقاً وشاملاً للأفكار الرئيسية.",
    "detailed": "اكتب ملخصاً تفصيلياً شاملاً لهذه المحاضرة، تناول كل عنوان ومفهوم رئيسي بالتوسع.",
    "bullets":  "استخرج النقاط الرئيسية من المحاضرة ورتّبها في قوائم واضحة بحسب المحاور.",
    "concepts": "استخرج المفاهيم الأساسية في المحاضرة واشرح كل مفهوم بشكل مختصر وواضح.",
    "exam":     "اكتب ملاحظات مراجعة مختصرة ومركّزة للطالب قبل الاختبار، مع إبراز المعلومات المهمة.",
}


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
            mode     = body.get("mode", "quick")

            if not pdf_text:
                return self._error(400, "pdf_text مطلوب")
            if mode not in SUMMARY_PROMPTS:
                return self._error(400, f"mode غير صالح. الخيارات: {list(SUMMARY_PROMPTS)}")

            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                return self._error(500, "مفتاح API غير مُعيَّن على الخادم")

            client = anthropic.Anthropic(api_key=api_key)

            system = "أنت مساعد جامعي عربي محترف متخصص في تلخيص المحاضرات الأكاديمية. اكتب بأسلوب واضح ومنظم، استخدم العناوين والنقاط."

            user = f"""{SUMMARY_PROMPTS[mode]}

محتوى المحاضرة:
{pdf_text[:13000]}"""

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            summary = response.content[0].text

            self.send_response(200)
            self._set_cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"summary": summary}, ensure_ascii=False).encode())

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
