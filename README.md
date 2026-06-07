# Wellness Tracker

Students preparing for exams such as NEET, JEE, CUET, CAT, GATE, UPSC, and various board examinations often face stress, anxiety, burnout, self-doubt, and uncertainty. Therefore I have developed an AI-powered emotional wellness app with image emotion analysis, therapeutic chat, metrics dashboard, guardian email alerts, and user authentication that helps students track their mood, identify stress triggers, reflect on their emotions, and receive personalized wellness support throughout their academic journey.

## Tech stack

| Layer | Stack |
|-------|--------|
| Frontend | React, Vite, Tailwind CSS, Recharts |
| Backend | FastAPI, SQLAlchemy, SQLite |
| AI | Google Gemini (`gemini-2.5-flash`) |
| Auth | JWT + bcrypt |

## Project structure

```
Wellnes Tracker/
├── backend/          # FastAPI API
│   ├── app/
│   ├── requirements.txt
│   └── .env.example
├── frontend/         # React UI
│   ├── src/
│   └── .env.example
├── project-docs/     # Design notes
└── render.yaml       # Optional Render deploy blueprint
```

## Local setup

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then edit .env with your keys
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env            # optional for local; defaults to localhost:8000
npm run dev
```

Open **http://localhost:5173**

### 3. Run tests

```bash
cd backend
source venv/bin/activate
pytest app/tests -v
```

## Environment variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `GEMINI_API_KEY` | For real AI | Google AI Studio key |
| `SECRET_KEY` | Production | JWT signing key (`openssl rand -hex 32`) |
| `ALLOWED_ORIGINS` | Production | Comma-separated frontend URLs for CORS |
| `GMAIL_ADDRESS` | For emails | Sender Gmail address |
| `GMAIL_APP_PASSWORD` | For emails | Google App Password |
| `DATABASE_URL` | Optional | Defaults to SQLite |

### Frontend (`frontend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_URL` | Production | e.g. `https://your-api.onrender.com/api/v1` |

## Deploy free (Render)

Recommended: **[Render](https://render.com)** free tier — backend + static frontend.

### Backend (Web Service)

1. New → **Web Service** → connect GitHub repo  
2. **Root directory:** `backend`  
3. **Build:** `pip install -r requirements.txt`  
4. **Start:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`  
5. Add env vars from `backend/.env.example`  
6. Set `ALLOWED_ORIGINS` to your frontend URL (e.g. `https://wellness-tracker-web.onrender.com`)

### Frontend (Static Site)

1. New → **Static Site** → same repo  
2. **Root directory:** `frontend`  
3. **Build:** `npm install && npm run build`  
4. **Publish directory:** `dist`  
5. Env var: `VITE_API_URL=https://YOUR-BACKEND.onrender.com/api/v1`  
6. Add rewrite rule: `/*` → `/index.html` (for client-side routing)

Or use the included `render.yaml` blueprint for one-click setup (rename services/URLs as needed).

> **Note:** Render free tier spins down after inactivity (cold starts ~30s). SQLite data may reset on redeploy — use Render Postgres for production persistence.

## Security checklist before publishing

- [ ] `.env` files are **not** committed (see `.gitignore`)
- [ ] `SECRET_KEY` set to a random value in production
- [ ] `GEMINI_API_KEY` and Gmail credentials only in host env vars
- [ ] `ALLOWED_ORIGINS` lists only your live frontend URL
- [ ] Never commit `wellness.db` or `venv/`

## Features

- User registration & login (JWT)
- Image emotion analysis with score validation
- Therapeutic chat with PII redaction
- 7-day metrics dashboard
- Weekly reports emailed to guardian
- High stress/anxiety threshold alerts via Gmail

## License

MIT (or your course/project license)
