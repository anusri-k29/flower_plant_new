from __future__ import annotations
import os
import requests

def plant_chat_reply(message: str, context_plant: str | None = None) -> str:
	"""Use an OpenAI-compatible Chat Completions API to answer plant-related queries."""
	api_key = os.getenv("OPENAI_API_KEY")
	base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
	model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
	if not api_key:
		return "Chatbot is not configured. Please set OPENAI_API_KEY."

	url = f"{base_url.rstrip('/')}/chat/completions"
	system_prompt = (
		"You are a helpful assistant specialized in botany and herbal information. "
		"Provide accurate, safety-conscious answers. If unsure, say so."
	)
	if context_plant:
		system_prompt += f" The current context plant is: {context_plant}."

	payload = {
		"model": model,
		"messages": [
			{"role": "system", "content": system_prompt},
			{"role": "user", "content": message},
		],
		"temperature": 0.2,
	}
	headers = {
		"Authorization": f"Bearer {api_key}",
		"Content-Type": "application/json",
	}
	try:
		resp = requests.post(url, json=payload, headers=headers, timeout=30)
		if resp.status_code == 200:
			data = resp.json()
			return data["choices"][0]["message"]["content"].strip()
		return f"Chat API error: {resp.status_code} {resp.text[:200]}"
	except Exception as e:
		return f"Chat error: {e}"
