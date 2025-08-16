import { useState } from "react";
import React from "react";

const API_URL = import.meta.env.VITE_API_URL;

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!text.trim()) return;

    // Add user message locally
    const userMessage = { sender: "user", text };
    setMessages(prev => [...prev, userMessage]);

    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/messages/create/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();

      if (data.reply) {
        setMessages(prev => [...prev, { sender: "bot", text: data.reply }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { sender: "bot", text: "Error: Could not get AI response." }]);
    } finally {
      setText("");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center p-4">
      <h1 className="text-2xl color-primary font-bold mb-4">AI Chatbot</h1>

      <div className="w-full max-w-md bg-white shadow rounded p-4 flex flex-col gap-2">
        <div className="flex flex-col gap-2 overflow-y-auto max-h-64 border p-2 rounded">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`p-2 rounded text-sm ${
                msg.sender === "user"
                  ? "bg-blue-100 self-end"
                  : "bg-green-100 self-start"
              }`}
            >
              <span className="font-semibold">
                {msg.sender === "user" ? "You" : "Bot"}:
              </span>{" "}
              {msg.text}
            </div>
          ))}
          {loading && (
            <div className="text-gray-500 italic text-sm">Bot is typing...</div>
          )}
        </div>

        <div className="flex gap-2 mt-2">
          <input
            value={text}
            onChange={e => setText(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            className="border p-2 rounded w-full"
            placeholder="Type a message..."
          />
          <button
            onClick={sendMessage}
            className="bg-red-500 hover:bg-blue-600 text-white px-4 rounded"
            disabled={loading}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
