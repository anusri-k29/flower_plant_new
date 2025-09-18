import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { chat } from '../api.js';

export default function Chatbot({ contextPlant }) {
	const [open, setOpen] = useState(false);
	const [messages, setMessages] = useState([{ role: 'assistant', content: 'Hi! Ask me anything about plants.' }]);
	const [input, setInput] = useState('');
	const [loading, setLoading] = useState(false);

	const send = async () => {
		if (!input.trim()) return;
		const userMsg = { role: 'user', content: input };
		setMessages((m) => [...m, userMsg]);
		setInput('');
		setLoading(true);
		try {
			const res = await chat(input, contextPlant);
			setMessages((m) => [...m, { role: 'assistant', content: res.reply }]);
		} catch (e) {
			setMessages((m) => [...m, { role: 'assistant', content: 'Error contacting chatbot.' }]);
		} finally {
			setLoading(false);
		}
	};

	return (
		<>
			<button className="chat-fab" onClick={() => setOpen((v) => !v)}>💬</button>
			<AnimatePresence>
				{open && (
					<motion.div
						className="chat-panel"
						initial={{ opacity: 0, y: 20 }}
						animate={{ opacity: 1, y: 0 }}
						exit={{ opacity: 0, y: 20 }}
					>
						<div className="chat-header">
							<strong>Plant Chatbot</strong>
							<button onClick={() => setOpen(false)}>✖</button>
						</div>
						<div className="chat-body">
							{messages.map((m, i) => (
								<div key={i} className={m.role === 'user' ? 'bubble user' : 'bubble'}>
									{m.content}
								</div>
							))}
							{loading && <div className="bubble">Thinking…</div>}
						</div>
						<div className="chat-input">
							<input
								value={input}
								onChange={(e) => setInput(e.target.value)}
								onKeyDown={(e) => e.key === 'Enter' ? send() : null}
								placeholder="Ask about plant care, toxicity, etc."
							/>
							<button onClick={send} disabled={loading}>Send</button>
						</div>
					</motion.div>
				)}
			</AnimatePresence>
		</>
	);
}
