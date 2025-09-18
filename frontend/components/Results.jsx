import React from 'react';
import { motion } from 'framer-motion';

export default function Results({ result, loading }) {
	if (loading) {
		return (
			<motion.div className="card" initial={{ opacity: 0.4 }} animate={{ opacity: 1 }}>
				<div className="spinner" /> Processing image...
			</motion.div>
		);
	}
	if (!result) {
		return (
			<motion.div className="card" initial={{ opacity: 0.4 }} animate={{ opacity: 1 }}>
				No result yet. Upload an image to begin.
			</motion.div>
		);
	}
	return (
		<motion.div className="card" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
			<h2>{result.plant_name}</h2>

			<section>
				<h3>Medicinal Properties</h3>
				{(result.medicinal_properties || []).length ? (
					<ul>{result.medicinal_properties.map((m, i) => <li key={i}>{m}</li>)}</ul>
				) : (
					<p>None found</p>
				)}
			</section>

			<section>
				<h3>Regions</h3>
				{(result.regions || []).length ? (
					<ul>{result.regions.map((r, i) => <li key={i}>{r}</li>)}</ul>
				) : (
					<p>Not specified</p>
				)}
			</section>

			<section>
				<h3>Facts</h3>
				{(result.facts || []).length ? (
					<ul>{result.facts.map((f, i) => <li key={i}>{f}</li>)}</ul>
				) : (
					<p>No facts available</p>
				)}
			</section>

			<section>
				<h3>Model Scores</h3>
				<pre className="pre">{JSON.stringify(result.scores, null, 2)}</pre>
			</section>
		</motion.div>
	);
}
