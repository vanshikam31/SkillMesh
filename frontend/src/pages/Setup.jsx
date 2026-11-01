import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { errorText } from "../api";
import { useAuth } from "../AuthContext";
import Logo from "../components/Logo";
import ProfileForm from "../components/ProfileForm";
import { useToast } from "../components/Toast";

export default function Setup() {
  const { user, setUser } = useAuth();
  const nav = useNavigate();
  const toast = useToast();
  const [saving, setSaving] = useState(false);

  const save = async (form) => {
    if (!form.offered.length || !form.wanted.length) return toast("Add at least one skill to teach and one to learn.");
    setSaving(true);
    try { const { data } = await api.put("/profile", form); setUser(data); nav("/discover"); }
    catch (e) { toast(errorText(e)); } finally { setSaving(false); }
  };
  return (
    <>
      <header className="top"><div className="brand"><Logo />SkillMesh</div></header>
      <main>
        <section className="setup card">
          <h2>Tell us about you</h2>
          <p className="sub">Add what you can teach and what you want to learn. We use this to find your peers.</p>
          <ProfileForm user={user} onSave={save} saving={saving} buttonText="Show my peers" />
        </section>
      </main>
    </>
  );
}
