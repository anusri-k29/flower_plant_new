import React, { useState } from 'react';
import { motion } from 'framer-motion';
import Uploader from '../components/Uploader.jsx';
import Results from '../components/Results.jsx';
import LanguageSelector from '../components/LanguageSelector.jsx';
import Chatbot from '../components/Chatbot.jsx';
import { predictPlant, fetchPlantInfo, translateText } from '../api.js';

export default function Home() {
	const [imageFile, setImageFile] = useState(null);
	const [loading, setLoading] = useState(false);
	const [result, setResult] = useState(null);
	const [lang, setLang] = useState('en');

	const handleUpload = async (file) => {
		setImageFile(file);
		setLoading(true);
		try {
			const prediction = await predictPlant(file);
			let combined = prediction;
			// Enrich with plant-info endpoint
			const info = await fetchPlantInfo(prediction.plant_name, lang);
			combined = { ...prediction, ...info };
			// Translate fields if user language != en
			if (lang !== 'en') {
				combined = {
					...combined,
					plant_name: await translateText(combined.plant_name || prediction.plant_name, lang),
					medicinal_properties: await Promise.all((combined.medicinal_properties || []).map(t => translateText(t, lang))),
					regions: await Promise.all((combined.regions || []).map(t => translateText(t, lang))),
					facts: await Promise.all((combined.facts || []).map(t => translateText(t, lang))),
				};
			}
			setResult(combined);
		} catch (e) {
			console.error(e);
			alert('Prediction failed. Check backend logs.');
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="container">
			<header className="header">
				<motion.h1 initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
					Plant Identifier
				</motion.h1>
				<LanguageSelector value={lang} onChange={setLang} />
			</header>

			<main className="main">
				<Uploader onUpload={handleUpload} loading={loading} />
				<Results result={result} loading={loading} />
			</main>

			<Chatbot contextPlant={result?.plant_name} />
		</div>
	);
}
