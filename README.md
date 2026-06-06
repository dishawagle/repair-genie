# 🧞 Repair Genie

AI-powered appliance repair assistant. Describe your appliance problem, get a diagnosis with root causes, safety checks, and a step-by-step fix guide. Built at the Vibe Coding Hackathon.

## Architecture

```
repair-genie-python/
├── backend/        # FastAPI — handles Anthropic API calls securely
│   ├── main.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/       # Streamlit — user interface
    ├── app.py
    ├── requirements.txt
    └── .streamlit/
        └── secrets.toml.example
```

## Local setup

### 1. Clone the repo
```bash
git clone https://github.com/dishawagle/repair-genie.git
cd repair-genie
```

### 2. Backend (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your Gemini API key
# Get one free at: https://aistudio.google.com/app/apikey

uvicorn main:app --reload --port 8000
```
Backend runs at `http://localhost:8000`. Test it at `http://localhost:8000/health`.

### 3. Frontend (Streamlit)
```bash
cd frontend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# secrets.toml already points to http://localhost:8000 for local dev

streamlit run app.py
```
Frontend runs at `http://localhost:8501`.

## Deploying to Streamlit Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Set **Main file path** to `frontend/app.py`
4. Under **Advanced settings → Secrets**, add:
   ```toml
   BACKEND_URL = "https://your-backend-url.com"
   ```
5. Deploy your FastAPI backend separately (Railway, Render, or Fly.io are free options)

## Deploying FastAPI (Render — free tier)

1. Create a new **Web Service** on [render.com](https://render.com)
2. Connect your GitHub repo
3. Set:
   - **Root directory:** `backend`
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variable: `GEMINI_API_KEY=your_key`
5. Copy the Render URL into your Streamlit Cloud secrets as `BACKEND_URL`

## Tech stack
- **Backend:** FastAPI + Google Generative AI SDK
- **Frontend:** Streamlit
- **AI:** Gemini 1.5 Flash
