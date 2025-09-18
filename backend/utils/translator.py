from __future__ import annotations
import os
import requests

def translate_text(text: str, target_lang: str) -> str:
	"""Translate using LibreTranslate-compatible API, if configured."""
	api_url = os.getenv("TRANSLATE_API_URL")
	if not api_url:
		return text
	payload = {"q": text, "target": target_lang}
	api_key = os.getenv("TRANSLATE_API_KEY", "")
	headers = {"Content-Type": "application/json"}
	if api_key:
		payload["api_key"] = api_key
	try:
		resp = requests.post(api_url, json=payload, timeout=15, headers=headers)
		if resp.status_code == 200:
			data = resp.json()
			translated = data.get("translatedText") or data.get("translated_text") or text
			return translated
	except Exception:
		return text
	return text
