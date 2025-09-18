from __future__ import annotations
import os
import csv
from typing import Any, Optional
import numpy as np
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env
load_dotenv()

# CORS
allowed_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(",") if o.strip()]

app = FastAPI(title="Plant Identifier API", version="1.0.0")
app.add_middleware(
	CORSMiddleware,
	allow_origins=allowed_origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

# Lazy TF import to speed cold start of imports
tf = None
keras = None
primary_model = None
secondary_model = None
class_labels: Optional[list[str]] = None

from utils.preprocess import load_image_bytes_to_array, softmax, topk_indices
from utils.plant_info import extract_plant_info
from utils.translator import translate_text
from utils.chatbot import plant_chat_reply

def _load_class_labels():
	global class_labels
	labels_path = os.getenv("CLASS_LABELS_PATH", "").strip()
	if not labels_path:
		class_labels = None
		return
	if not os.path.exists(labels_path):
		class_labels = None
		return
	with open(labels_path, "r", encoding="utf-8") as f:
		reader = csv.reader(f)
		# Allow either one-per-line or CSV with first column as label
		labels = []
		for row in reader:
			if not row:
				continue
			labels.append(row[0].strip())
	class_labels = labels or None

@app.on_event("startup")
def on_startup():
	global tf, keras, primary_model, secondary_model
	# Import TF / Keras at startup
	import tensorflow as _tf
	from tensorflow import keras as _keras
	tf = _tf
	keras = _keras

	model_primary_path = os.getenv("MODEL_PRIMARY_PATH", "./models/model_primary.h5")
	model_secondary_path = os.getenv("MODEL_SECONDARY_PATH", "./models/model_secondary.h5")

	if not os.path.exists(model_primary_path):
		raise RuntimeError(f"Primary model not found at {model_primary_path}")
	if not os.path.exists(model_secondary_path):
		raise RuntimeError(f"Secondary model not found at {model_secondary_path}")

	primary_model = keras.models.load_model(model_primary_path, compile=False)
	secondary_model = keras.models.load_model(model_secondary_path, compile=False)

	_load_class_labels()

@app.get("/health")
def health():
	return {"status": "ok"}

class TranslateRequest(BaseModel):
	text: str
	targetLang: str

class ChatRequest(BaseModel):
	message: str
	contextPlant: Optional[str] = None

def _predict_single(model, image_array: np.ndarray) -> dict[str, Any]:
	"""Run prediction on a single model and return top-3 probabilities and labels."""
	preds = model.predict(image_array, verbose=0)
	if preds.ndim == 2:
		preds = preds[0]
	elif preds.ndim == 1:
		preds = preds
	else:
		preds = preds.reshape(-1)
	probs = softmax(preds)
	top3_idx = topk_indices(probs, 3)
	top3 = []
	for idx in top3_idx:
		label = class_labels[idx] if class_labels and idx < len(class_labels) else f"class_{idx}"
		top3.append({"label": label, "prob": float(probs[idx])})
	return {
		"top3": top3,
		"raw": [float(x) for x in probs.tolist()],
	}

@app.post("/predict")
async def predict(image: UploadFile = File(...)):
	if not primary_model or not secondary_model:
		raise HTTPException(status_code=503, detail="Models not loaded")

	content = await image.read()
	if not content:
		raise HTTPException(status_code=400, detail="Empty image upload")

	try:
		img_arr = load_image_bytes_to_array(content)
	except Exception as e:
		raise HTTPException(status_code=400, detail=f"Invalid image: {e}")

	primary = _predict_single(primary_model, img_arr)
	secondary = _predict_single(secondary_model, img_arr)

	# Derive a final plant name by voting top-1 label
	primary_top = primary["top3"][0]["label"] if primary["top3"] else "unknown"
	secondary_top = secondary["top3"][0]["label"] if secondary["top3"] else "unknown"
	plant_name = primary_top if primary_top == secondary_top else primary_top  # simple preference

	extra_info = extract_plant_info(plant_name)

	return {
		"plant_name": extra_info.get("plant_name", plant_name),
		"scores": {
			"primary": primary,
			"secondary": secondary,
		},
		"medicinal_properties": extra_info.get("medicinal_properties", []),
		"regions": extra_info.get("regions", []),
		"facts": extra_info.get("facts", []),
	}

@app.get("/plant-info")
def plant_info(name: str = Query(..., min_length=1), lang: str = Query("en")):
	info = extract_plant_info(name)
	# Optionally translate summary fields
	if lang and lang != "en":
		info["plant_name"] = translate_text(info["plant_name"], lang) if info.get("plant_name") else info.get("plant_name")
		info["medicinal_properties"] = [translate_text(x, lang) for x in info.get("medicinal_properties", [])]
		info["regions"] = [translate_text(x, lang) for x in info.get("regions", [])]
		info["facts"] = [translate_text(x, lang) for x in info.get("facts", [])]
	return info

@app.post("/translate")
def translate(req: TranslateRequest):
	return {"text": translate_text(req.text, req.targetLang)}

@app.post("/chat")
def chat(req: ChatRequest):
	reply = plant_chat_reply(req.message, req.contextPlant)
	return {"reply": reply}

if __name__ == "__main__":
	import uvicorn
	port = int(os.getenv("PORT", "8000"))
	uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
