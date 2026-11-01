import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { errorText } from "../api";
import { useAuth } from "../AuthContext";
import Logo from "../components/Logo";

const TITLES = { signup: "Create your account", signin: "Welcome back", forgot: "Reset your password" };
const BUTTONS = { signup: "Create account", signin: "Sign in", forgot: "Send reset link" };

export default function Landing() {
  const { authenticate } = useAuth();
  const nav = useNavigate();
  const [popup, setPopup] = useState(false);
  const [mode, setMode] = useState("signup");            // signup | signin | forgot
  const [f, setF] = useState({ name: "", email: "", password: "" });
  const [err, setErr] = useState("");
  const [taken, setTaken] = useState(false);              // true when the email already has an account
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(null);                 // answer of /auth/forgot-password

  useEffect(() => { const t = setTimeout(() => setPopup(true), 2000); return () => clearTimeout(t); }, []);   // popup after 2 seconds

  const go = (m) => { setMode(m); setErr(""); setTaken(false); setSent(null); };   // keeps the typed email
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    const email = f.email.trim(), name = f.name.trim(), password = f.password;
    setTaken(false);
    if (!/^\S+@\S+\.\S+$/.test(email)) return setErr("Enter a valid email address.");
    if (mode === "signup" && !name) return setErr("Enter your name.");
    if (mode !== "forgot" && password.length < 6) return setErr(mode === "signup" ? "Use at least 6 characters for the password." : "Enter your password.");
    setBusy(true); setErr("");
    try {
      if (mode === "forgot") { const { data } = await api.post("/auth/forgot-password", { email }); setSent(data); return; }
      const user = mode === "signup" ? await authenticate("/auth/register", { name, email, password }) : await authenticate("/auth/login", { email, password });
      nav(user.setup_done ? "/discover" : "/setup");
    } catch (ex) {
      setErr(errorText(ex));
      setTaken(ex?.response?.status === 409);
    } finally { setBusy(false); }
  };

  return (
    <>
      <div className="splash"><Logo className="logo" /><h1>SkillMesh</h1><p>Learn what you want. Teach what you know.</p></div>
      {popup && (
        <div className="scrim">
          <div className="auth card" role="dialog" aria-modal="true" aria-labelledby="at">
            {mode !== "forgot" && (
              <div className="seg">
                <button type="button" aria-pressed={mode === "signin"} onClick={() => go("signin")}>Sign in</button>
                <button type="button" aria-pressed={mode === "signup"} onClick={() => go("signup")}>Sign up</button>
              </div>
            )}
            <h2 id="at">{TITLES[mode]}</h2>

            {sent ? (
              <div>
                <p className="ok" role="status">{sent.message}</p>
                {sent.dev_reset_link && (
                  <div className="devbox">
                    <p>Email sending is not set up yet, so here is your link (development mode only):</p>
                    <a className="btn primary wide" href={sent.dev_reset_link}>Set a new password</a>
                  </div>
                )}
                <button type="button" className="link-btn" onClick={() => go("signin")}>Back to sign in</button>
              </div>
            ) : (
              <form onSubmit={submit} noValidate>
                {mode === "forgot" && <p className="sub">Enter your email and we will send you a link to set a new password.</p>}
                {mode === "signup" && <label className="field">Name<input type="text" value={f.name} onChange={set("name")} autoComplete="name" autoFocus /></label>}
                <label className="field">Email<input type="text" value={f.email} onChange={set("email")} inputMode="email" autoComplete="email" autoFocus={mode !== "signup"} /></label>
                {mode !== "forgot" && (
                  <label className="field">Password<input type="password" value={f.password} onChange={set("password")} autoComplete={mode === "signup" ? "new-password" : "current-password"} /></label>
                )}
                <p className="err" role="alert">
                  {err}
                  {taken && <button type="button" className="link-btn" onClick={() => go("signin")}>Sign in instead</button>}
                </p>
                <button className="btn primary wide" type="submit" disabled={busy}>{busy ? "Please wait..." : BUTTONS[mode]}</button>
                {mode === "signin" && <div className="below"><button type="button" className="link-btn" onClick={() => go("forgot")}>Forgot password?</button></div>}
                {mode === "forgot" && <div className="below"><button type="button" className="link-btn" onClick={() => go("signin")}>Back to sign in</button></div>}
              </form>
            )}
          </div>
        </div>
      )}
    </>
  );
}
