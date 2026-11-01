import { useCallback, useEffect, useState } from "react";
import api, { errorText } from "../api";
import { useAuth } from "../AuthContext";
import MeshGraph from "../components/MeshGraph";
import PeerCard from "../components/PeerCard";
import ProfileForm from "../components/ProfileForm";
import { useToast } from "../components/Toast";

export default function Discover() {
  const { user, setUser } = useAuth();
  const toast = useToast();
  const [matches, setMatches] = useState(null);
  const [selected, setSelected] = useState(null);
  const [saving, setSaving] = useState(false);

  const load = useCallback(() => api.get("/recommendations", { params: { n: 10 } }).then((r) => setMatches(r.data)).catch((e) => toast(errorText(e))), [toast]);
  useEffect(() => { load(); }, [load]);

  const select = (id) => {
    setSelected(id);
    document.getElementById("peer-" + id)?.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "center" });
  };
  const send = async (peer) => {
    try { await api.post("/requests", { receiver_id: peer.id }); toast(`Request sent to ${peer.name}.`); load(); }
    catch (e) { toast(errorText(e)); }
  };
  const save = async (form) => {
    setSaving(true);
    try { const { data } = await api.put("/profile", form); setUser(data); toast("Profile saved. Matches updated."); await load(); }
    catch (e) { toast(errorText(e)); } finally { setSaving(false); }
  };

  return (
    <div className="layout">
      <aside className="panel"><ProfileForm key={user.id} user={user} onSave={save} saving={saving} buttonText="Save and update matches" title="Your profile" /></aside>
      <section>
        <div className="meshcard">
          <div className="meshhead"><h2>Your mesh</h2><p className="sub">Thicker lines are stronger matches. Select a person to see why.</p></div>
          {matches && matches.length > 0 && <MeshGraph matches={matches} selected={selected} onSelect={select} />}
        </div>
        <h2 className="listh">Recommended peers</h2>
        {matches === null && <p className="empty">Finding your peers...</p>}
        {matches && matches.length === 0 && <p className="empty card">No peers yet. Run <code>python backend/seed.py</code> to add sample students, or invite classmates to sign up.</p>}
        {matches && matches.map((m) => <PeerCard key={m.peer.id} match={m} selected={selected === m.peer.id} onSend={send} />)}
      </section>
    </div>
  );
}
