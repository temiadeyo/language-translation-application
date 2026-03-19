import { useEffect, useState, useCallback } from "react";
import "./App.css";

import { withAuthenticator } from "@aws-amplify/ui-react";
import "@aws-amplify/ui-react/styles.css";

import { signOut, fetchAuthSession } from "aws-amplify/auth";

const BASE_URL = "https://tdzdkoi6of.execute-api.us-east-1.amazonaws.com";

function App() {
  const [text, setText] = useState("");
  const [language, setLanguage] = useState("French");
  const [result, setResult] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const [sidebarOpen, setSidebarOpen] = useState(() => {
    const saved = localStorage.getItem("sidebarOpen");
    return saved ? JSON.parse(saved) : false;
  });

  useEffect(() => {
    localStorage.setItem("sidebarOpen", JSON.stringify(sidebarOpen));
  }, [sidebarOpen]);

  async function getToken() {
    const session = await fetchAuthSession();
    return session.tokens.idToken.toString();
  }

  const loadHistory = useCallback(async () => {
    try {
      const token = await getToken();

      const res = await fetch(`${BASE_URL}/history`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      if (!res.ok) {
        throw new Error("History request failed");
      }

      const data = await res.json();

      const sorted = [...data].sort(
        (a, b) => new Date(b.timestamp) - new Date(a.timestamp)
      );

      setHistory(sorted);
    } catch (err) {
      console.error(err);
    }
  }, []);

  async function translate() {
    if (!text.trim()) return;

    try {
      setLoading(true);

      const token = await getToken();

      const res = await fetch(`${BASE_URL}/translate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          text_original: text,
          language: language
        })
      });

      if (!res.ok) {
        throw new Error("Translation request failed");
      }

      const data = await res.json();

      setResult(data.translatedText);
      setText("");

      await loadHistory();
    } catch (err) {
      console.error(err);
      setResult("Something went wrong. Try again.");
    } finally {
      setLoading(false);
    }
  }

  async function deleteItem(timestamp) {
    try {
      const token = await getToken();

      const res = await fetch(`${BASE_URL}/history/${timestamp}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      if (!res.ok) {
        throw new Error("Delete failed");
      }

      setHistory(prev =>
        prev.filter(item => item.timestamp !== timestamp)
      );
    } catch (err) {
      console.error(err);
    }
  }

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  return (
    <div className="app-container">

      <button
        className="logout-btn"
        onClick={() => signOut()}
      >
        Log out
      </button>

      <button
        className="toggle-btn"
        onClick={() => setSidebarOpen(open => !open)}
      >
        {sidebarOpen ? "✕" : "☰"}
      </button>

      <div className={`sidebar ${sidebarOpen ? "open" : ""}`}>
        <h2>History</h2>

        {history.map(item => (
          <div key={item.timestamp} className="history-item">
            <div className="history-text">
              <strong>{item.originalText}</strong>
              <div>{item.translatedText}</div>
              <small>{item.language}</small>
            </div>

            <button
              className="delete-btn"
              onClick={() => deleteItem(item.timestamp)}
            >
              🗑
            </button>
          </div>
        ))}
      </div>

      <div className="main">
        <div className="card">

          <h1>Language Translator</h1>
          <p className="subtitle">Translate your text instantly</p>

          <textarea
            placeholder="Type or paste text here..."
            value={text}
            onChange={e => setText(e.target.value)}
          />

          <select
            value={language}
            onChange={e => setLanguage(e.target.value)}
          >
            <option>English</option>
            <option>French</option>
            <option>Spanish</option>
            <option>German</option>
            <option>Japanese</option>
          </select>

          <button onClick={translate} disabled={loading}>
            {loading ? "Translating..." : "Translate"}
          </button>

          {loading && <div className="spinner"></div>}

          <div className="result-box">
            {result}
          </div>

        </div>
      </div>
    </div>
  );
}

export default withAuthenticator(App);