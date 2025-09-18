import React, { useRef } from 'react';
import { motion } from 'framer-motion';

export default function Uploader({ onUpload, loading }) {
	const inputRef = useRef(null);

	const onFileChange = (e) => {
		const file = e.target.files?.[0];
		if (file) onUpload(file);
	};

	return (
		<motion.div className="card" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
			<h2>Upload or Capture</h2>
			<input
				ref={inputRef}
				type="file"
				accept="image/*"
				capture="environment"
				onChange={onFileChange}
				disabled={loading}
			/>
			<p className="hint">Use your camera or upload an image of a plant/flower.</p>
		</motion.div>
	);
}
