# UniMind AI 🎓

مساعد جامعي ذكي مدعوم بـ Claude AI — لخّص محاضراتك، اسأل أسئلة، وأنشئ اختبارات في ثوانٍ.

---

## Project Structure

```
unimind-vercel/
├── api/
│   ├── ask.py        # POST /api/ask      — Q&A
│   ├── summary.py    # POST /api/summary  — Summaries
│   └── quiz.py       # POST /api/quiz     — Quiz generation
├── public/
│   └── index.html    # Full frontend (HTML/CSS/JS)
├── vercel.json       # Vercel routing config
├── requirements.txt  # Python dependencies
└── README.md
```

---

## Deploy to Vercel

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial UniMind AI"
git remote add origin https://github.com/YOUR_USERNAME/unimind-ai.git
git push -u origin main
```

### 2. Import on Vercel
1. Go to [vercel.com](https://vercel.com) → **Add New Project**
2. Import your GitHub repo
3. Framework Preset: **Other**
4. Click **Deploy**

### 3. Add Environment Variable
1. Go to your project → **Settings → Environment Variables**
2. Add:
   - **Name**: `ANTHROPIC_API_KEY`
   - **Value**: `sk-ant-api03-...` (your key from console.anthropic.com)
3. Click **Save**
4. Go to **Deployments** → click the three dots → **Redeploy**

That's it! Your app is live. Users never see or enter the API key.

---

## API Endpoints

| Endpoint | Method | Body | Response |
|---|---|---|---|
| `/api/ask` | POST | `{pdf_text, question}` | `{answer}` |
| `/api/summary` | POST | `{pdf_text, mode}` | `{summary}` |
| `/api/quiz` | POST | `{pdf_text, num_questions, difficulty}` | `{quiz}` |

### Summary modes
`quick` · `detailed` · `bullets` · `concepts` · `exam`

### Quiz difficulty
`easy` · `medium` · `hard`

---

## Local Development

```bash
pip install -r requirements.txt
vercel dev   # requires Vercel CLI + .env.local with ANTHROPIC_API_KEY
```

Or set the env var manually:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
vercel dev
```

---

## Tech Stack
- **Frontend**: Vanilla HTML/CSS/JS · pdf.js for client-side PDF extraction
- **Backend**: Python serverless functions (Vercel)
- **AI**: Anthropic Claude Sonnet via server-side API
- **Deployment**: Vercel
