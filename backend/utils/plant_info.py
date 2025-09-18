from __future__ import annotations
import requests
from typing import Any

WIKI_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"

def fetch_wikipedia_summary(title: str) -> dict[str, Any] | None:
	"""Fetch a concise summary for a page title from Wikipedia REST API."""
	try:
		resp = requests.get(WIKI_SUMMARY_URL.format(title=title), timeout=10)
		if resp.status_code == 200:
			return resp.json()
	except Exception:
		return None
	return None

def extract_plant_info(plant_name: str) -> dict[str, Any]:
	"""Best-effort extraction of info from Wikipedia summary."""
	summary = fetch_wikipedia_summary(plant_name)
	if not summary:
		return {
			"plant_name": plant_name,
			"medicinal_properties": [],
			"regions": [],
			"facts": [],
			"source": "wikipedia",
		}
	extract = summary.get("extract", "") or ""
	# Heuristic placeholders; for production enrich using Wikidata or curated KB.
	medicinal = []
	regions = []
	facts = []
	if "poison" in extract.lower():
		facts.append("May be poisonous; handle with care.")
	if "medicinal" in extract.lower() or "traditional medicine" in extract.lower():
		medicinal.append("Reported traditional or medicinal uses; verify with local sources.")
	if "tropical" in extract.lower():
		regions.append("Tropical regions")
	if "temperate" in extract.lower():
		regions.append("Temperate regions")
	if not facts and extract:
		facts.append(extract[:280] + ("..." if len(extract) > 280 else ""))
	return {
		"plant_name": plant_name,
		"medicinal_properties": medicinal,
		"regions": regions,
		"facts": facts,
		"source": "wikipedia",
	}
