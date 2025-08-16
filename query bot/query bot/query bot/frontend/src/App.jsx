import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import React from "react"
import Chat from "../src/pages/chat";

export default function App() {
  return (
    <Router>
      <nav className="bg-gray-800 p-4 text-white">
        <div className="max-w-4xl mx-auto flex gap-4">
          <Link to="/" className="hover:underline">Home</Link>
          <Link to="/chat" className="hover:underline">Chat</Link>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto mt-6">
        <Routes>
          <Route path="/" element={<h1 className="text-xl font-bold">Welcome to the Bot App</h1>} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </div>
    </Router>
  );
}