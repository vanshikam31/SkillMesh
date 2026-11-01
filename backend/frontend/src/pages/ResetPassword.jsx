import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import api, { errorText } from "../api";
import Logo from "../components/Logo";

export default function ResetPassword() {
  const [params] = useSearchParams();
  const token = params.get("token") || "";
  const nav = useNavigate();
  const [pw, setPw] = useState("");
  const [pw2, setPw2] = useState("");
  const [err, setErr] = useState("");
  const [done, setDone] = useState(false);
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (pw.length < 6) return setErr("Use at least 6 characters for the password.");
    if (pw !== pw2) return setErr("The two passwords do not match.");
    setBusy(true); setErr("");
    try { await api.post("/auth/reset-password", { token, new_password: pw }); setDone(true); }
    catch (ex) { setErr(errorText(ex)); } finally { setBusy(false); }
  };

  return (
    <>
      <header className="top"><div className="brand"><Logo />SkillMesh</div></header>
      <main>
        <section className="setup card" style={{ maxWidth: 440 }}>
          <h2>Set a new password</h2>
          {!token ? (
            <p className="empty">This link has no reset code. Go back and use <strong>Forgot password?</strong> to get a new link.</p>
          ) : done ? (
            <>
              <p className="ok" role="status">Password updated. You can sign in now.</p>
              <button className="btn primary wide" onClick={() => nav("/")}>Go to sign in</button>
            </>
          ) : (
            <form onSubmit={submit} noValidate>
              <label className="field">New password<input type="password" value={pw} onChange={(e) => setPw(e.target.value)} autoComplete="new-password" autoFocus /></label>
              <label className="field">Confirm new password<input type="password" value={pw2} onChange={(e) => setPw2(e.target.value)} autoComplete="new-password" /></label>
              <p className="err" role="alert">{err}</p>
              <button className="btn primary wide" type="submit" disabled={busy}>{busy ? "Please wait..." : "Update password"}</button>
            </form>
          )}
          <p className="hint" style={{ marginTop: 14 }}><Link to="/" className="link-btn">Back to home</Link></p>
        </section>
      </main>
    </>
  );
}
