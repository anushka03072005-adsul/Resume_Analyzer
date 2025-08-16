import React, { useState } from "react";
import { supabase } from "./supabaseClient";
import "./App.css";

export default function App() {
  const [file, setFile] = useState(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [user, setUser] = useState(null);
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState("");
  const [pdfUrl, setPdfUrl] = useState("");

  const handleSignup = async () => {
    if (!email || !password) return alert("Enter email and password");
    const { error } = await supabase.auth.signUp({ email, password });
    if (error) alert(error.message);
    else {
      alert("Signup successful! Check your email.");
      setIsLogin(true);
    }
  };

  const handleLogin = async () => {
    if (!email || !password) return alert("Enter email and password");
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) alert(error.message);
    else {
      const loggedUser = data.user || data.session?.user;
      setUser(loggedUser);
      alert("Login successful!");
    }
  };

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const uploadResume = async () => {
    if (!user) return alert("Please log in first");
    if (!file) return alert("Please select a file first");

    setLoading(true);
    const fileName = `${user.id}/${file.name}`;
    const { error } = await supabase.storage.from("resumes").upload(fileName, file, { overwrite: true });

    if (error) {
      alert("Upload failed");
      console.error(error);
      setLoading(false);
      return;
    }

    alert("File uploaded!");

    // Send to Flask backend
    const formData = new FormData();
    formData.append("resume", file);
    formData.append("job_description", "Python backend developer");
    formData.append("user_id", user.id);

    try {
      const response = await fetch("http://localhost:5000/analyze", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      setAnalysis(data.analysis);
      setPdfUrl(data.pdf_url || "");
    } catch (err) {
      console.error(err);
      alert("Resume analysis failed.");
    }

    setLoading(false);
  };

  const downloadFile = (url, name) => {
    const link = document.createElement("a");
    link.href = url;
    link.download = name;
    link.click();
  };

  return (
    <div className="container">
      <h1 className="title">Resume Analyzer</h1>

      {!user && (
        <div className="card auth-card">
          <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className="input-field" />
          <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} className="input-field" />
          {isLogin ? (
            <div>
              <button onClick={handleLogin} className="btn-primary">Login</button>
              <p className="toggle-text">Don’t have an account? <span onClick={() => setIsLogin(false)}>Sign up</span></p>
            </div>
          ) : (
            <div>
              <button onClick={handleSignup} className="btn-primary">Sign Up</button>
              <p className="toggle-text">Already have an account? <span onClick={() => setIsLogin(true)}>Login</span></p>
            </div>
          )}
        </div>
      )}

      {user && (
        <div className="card upload-card">
          <p>Logged in as: {user.email}</p>
          <input type="file" onChange={handleFileChange} className="input-field" />
          {file && <p>Selected file: {file.name}</p>}
          <button onClick={uploadResume} disabled={loading} className="btn-primary">
            {loading ? "Uploading..." : "Upload & Analyze Resume"}
          </button>

          {analysis && (
            <div className="analysis-card-wrapper">
              <div className="analysis-card">
                <h2>Analysis Result:</h2>
                <pre>{analysis}</pre>

                {pdfUrl && (
                  <button
                    className="btn-primary"
                    onClick={() => downloadFile(pdfUrl, `${file.name}_analysis.pdf`)}
                    style={{ marginTop: "15px" }}
                  >
                    Download Analysis PDF
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
