## Plant Identifier (React PWA + FastAPI)

- Frontend: React + Vite, PWA installable
- Backend: FastAPI, loads Keras .h5 models on startup
- Endpoints: /predict, /plant-info, /translate, /chat
- Ready for Render/Vercel/Railway

### Structure
See `plant-identifier-app/` layout in the main instructions.

### Model Files
Put your .h5 files in `backend/models`:
- `backend/models/model_primary.h5`
- `backend/models/model_secondary.h5`
Configure with env vars if needed.

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Put .h5 into backend/models/
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
