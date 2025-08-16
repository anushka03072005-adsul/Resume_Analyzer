import React, { useState } from "react";
import { supabase } from "./supabaseClient";

export default function Auth() {
  const [email, setEmail] = useState("");

  const handleLogin = async () => {
    const { error } = await supabase.auth.signInWithOtp({ email });
    if (error) console.error("Error:", error.message);
    else alert("Check your email for the login link!");
  };

  return (
    <div>
      <h2>Login / Sign Up</h2>
      <input
        type="email"
        placeholder="Enter your email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <button onClick={handleLogin}>Send Magic Link</button>
    </div>
  );
}
