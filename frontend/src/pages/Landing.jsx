import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { errorText } from "../api";
import { useAuth } from "../AuthContext";
import Logo from "../components/Logo";

export default function Landing() {
  const { authenticate } = useAuth();
  const nav = useNavigate();
  const [popup, setPopup] = useState(false);
  const [mode, setMode] = useState("signup");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => { const t = setTimeout(() => setPopup(true), 2000); return () => clearTimeout(t); }, []);   // popup after 2 seconds

  const submit = async (e) => {
    e.preventDefault();
    const f = new FormData(e.target);
    const email = String(f.get("email")).trim(), password = String(f.get("password")), name = String(f.get("name") || "").trim();
    if (!/^\S+@\S+\.\S+$/.test(email)) return setErr("Enter a valid email address.");
    if (mode === "signup" && !name) return setErr("Enter your name.");
    if (mode === "signup" && password.length < 6) return setErr("Use at least 6 characters for the password.");
    setBusy(true); setErr("");
    try {
      const user = mode === "signup" ? await authenticate("/auth/register", { name, email, password }) : await authenticate("/auth/login", { email, password });
      nav(user.setup_done ? "/discover" : "/setup");
    } catch (ex) { setErr(errorText(ex)); } finally { setBusy(false); }
  };

  return (
    <>
      <div className="splash"><Logo className="logo" /><h1>SkillMesh</h1><p>Learn what you want. Teach what you know.</p></div>
      {popup && (
        <div className="scrim">
          <div className="auth card" role="dialog" aria-modal="true" aria-labelledby="at">
            <div className="seg">
              <button type="button" aria-pressed={mode === "signin"} onClick={() => { setMode("signin"); setErr(""); }}>Sign in</button>
              <button type="button" aria-pressed={mode === "signup"} onClick={() => { setMode("signup"); setErr(""); }}>Sign up</button>
            </div>
            <h2 id="at">{mode === "signup" ? "Create your account" : "Welcome back"}</h2>
            <form onSubmit={submit} noValidate key={mode}>
              {mode === "signup" && <label className="field">Name<input type="text" name="name" autoComplete="name" autoFocus /></label>}
              <label className="field">Email<input type="text" name="email" inputMode="email" autoComplete="email" autoFocus={mode === "signin"} /></label>
              <label className="field">Password<input type="password" name="password" autoComplete={mode === "signup" ? "new-password" : "current-password"} /></label>
              <p className="err" role="alert">{err}</p>
              <button className="btn primary wide" type="submit" disabled={busy}>{mode === "signup" ? "Create account" : "Sign in"}</button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
