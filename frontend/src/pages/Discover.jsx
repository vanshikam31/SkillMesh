import { useCallback, useEffect, useState } from "react";
import api, { errorText } from "../api";
import { useAuth } from "../AuthContext";
import MeshGraph from "../components/MeshGraph";
import PeerCard from "../components/PeerCard";
import ProfileForm from "../components/ProfileForm";
import { useToast } from "../components/Toast";

const NO_FILTERS = { q: "", category: "", offered: "", wanted: "" };

export default function Discover() {
  const { user, setUser } = useAuth();
  const toast = useToast();
  const [top, setTop] = useState(null);          // best overall matches, drawn in the mesh graph
  const [mutual, setMutual] = useState(null);    // two-way matches
  const [explore, setExplore] = useState(null);  // everybody else, filtered
  const [categories, setCategories] = useState([]);
  const [filters, setFilters] = useState(NO_FILTERS);
  const [selected, setSelected] = useState(null);
  const [saving, setSaving] = useState(false);

  const fail = (e) => toast(errorText(e));
  const loadTop = useCallback(() => api.get("/recommendations", { params: { n: 10 } }).then((r) => setTop(r.data)).catch(fail), []);        // eslint-disable-line
  const loadMutual = useCallback(() => api.get("/recommendations/mutual").then((r) => setMutual(r.data)).catch(fail), []);                  // eslint-disable-line
  const loadExplore = useCallback(() => api.get("/recommendations/explore", { params: filters }).then((r) => setExplore(r.data)).catch(fail), [filters]);   // eslint-disable-line
  const reloadAll = () => { loadTop(); loadMutual(); loadExplore(); };

  useEffect(() => { loadTop(); loadMutual(); api.get("/skills/categories").then((r) => setCategories(r.data)).catch(() => {}); }, [loadTop, loadMutual]);
  useEffect(() => { const t = setTimeout(loadExplore, 300); return () => clearTimeout(t); }, [loadExplore]);     // wait until the person stops typing

  const select = (id) => {
    setSelected(id);
    document.getElementById("peer-" + id)?.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth", block: "center" });
  };
  const send = async (peer) => {
    try {
      const { data } = await api.post("/requests", { receiver_id: peer.id });
      toast(data.status === "accepted" ? `${peer.name} accepted your request. Open Sessions to chat.` : `Request sent to ${peer.name}.`);
      reloadAll();
    } catch (e) { fail(e); }
  };
  const save = async (form) => {
    setSaving(true);
    try { const { data } = await api.put("/profile", form); setUser(data); toast("Profile saved. Matches updated."); reloadAll(); }
    catch (e) { fail(e); } finally { setSaving(false); }
  };
  const setFilter = (k) => (e) => setFilters((f) => ({ ...f, [k]: e.target.value }));
  const filtersOn = Object.values(filters).some(Boolean);

  return (
    <div className="layout">
      <aside className="panel"><ProfileForm key={user.id} user={user} onSave={save} saving={saving} buttonText="Save and update matches" title="Your profile" /></aside>
      <section>
        <div className="meshcard">
          <div className="meshhead"><h2>Your mesh</h2><p className="sub">Thicker lines are stronger matches. Select a person to see why.</p></div>
          {top && top.length > 0 && <MeshGraph matches={top} selected={selected} onSelect={select} />}
        </div>

        <h2 className="listh">Mutual Skill Matches {mutual && <span className="count">{mutual.length}</span>}</h2>
        <p className="sub" style={{ marginBottom: 12 }}>They offer what you want, and they want what you offer. A fair two-way exchange.</p>
        {mutual === null && <p className="empty">Finding your matches...</p>}
        {mutual && mutual.length === 0 && <p className="empty card">No two-way matches yet. Explore other skills below, or add more skills to your profile.</p>}
        {mutual && mutual.map((m) => <PeerCard key={m.peer.id} match={m} selected={selected === m.peer.id} onSend={send} />)}

        <h2 className="listh" style={{ marginTop: 28 }}>Explore Other Skills {explore && <span className="count">{explore.length}</span>}</h2>
        <p className="sub" style={{ marginBottom: 12 }}>People whose skills do not match both ways. See what you could learn from them or teach them.</p>
        <div className="filters" role="search">
          <input type="search" placeholder="Search by username" value={filters.q} onChange={setFilter("q")} aria-label="Search by username" />
          <select value={filters.category} onChange={setFilter("category")} aria-label="Skill category">
            <option value="">All categories</option>
            {categories.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
          <input type="text" placeholder="They offer..." value={filters.offered} onChange={setFilter("offered")} aria-label="Filter by offered skill" />
          <input type="text" placeholder="They want..." value={filters.wanted} onChange={setFilter("wanted")} aria-label="Filter by wanted skill" />
          {filtersOn && <button className="btn small" onClick={() => setFilters(NO_FILTERS)}>Clear</button>}
        </div>
        {explore === null && <p className="empty">Loading...</p>}
        {explore && explore.length === 0 && (
          <p className="empty card">{filtersOn ? "Nobody matches these filters. Try clearing them." : "No other students yet. Invite classmates to sign up, or run python backend/seed.py for sample students."}</p>
        )}
        {explore && explore.map((m) => <PeerCard key={m.peer.id} match={m} selected={selected === m.peer.id} onSend={send} />)}
      </section>
    </div>
  );
}
