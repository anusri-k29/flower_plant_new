import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function predictPlant(file) {
  const form = new FormData();
  form.append('image', file);
  const res = await axios.post(`${API_BASE}/predict`, form, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return res.data;
}

export async function fetchPlantInfo(name, lang='en') {
  const res = await axios.get(`${API_BASE}/plant-info`, { params: { name, lang } });
  return res.data;
}

export async function translateText(text, targetLang) {
  if (!text) return '';
  const res = await axios.post(`${API_BASE}/translate`, { text, targetLang });
  return res.data.text;
}

export async function chat(message, contextPlant) {
  const res = await axios.post(`${API_BASE}/chat`, { message, contextPlant });
  return res.data;
}
