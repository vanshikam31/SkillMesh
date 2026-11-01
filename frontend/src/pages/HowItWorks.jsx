import { useEffect, useState } from "react";
import api from "../api";

const W = [["skill", "Teaches what you want"], ["reverse", "Wants what you offer"], ["exp", "Experience fit"], ["avail", "Shared free time"], ["rating", "Peer rating"]];
const DEFAULTS = { skill: 0.4, reverse: 0.2, exp: 0.15, avail: 0.15, rating: 0.1 };
const Bar = ({ label, v, cls }) => (
  <div className="ebar"><span>{label}</span><div className="track"><i className={cls} style={{ width: `${Math.round(v * 100)}%` }} /></div><b>{Math.round(v * 100)}%</b></div>
);

export default function HowItWorks() {
  const [w, setW] = useState(DEFAULTS);
  const [k, setK] = useState(5);
  const [ev, setEv] = useState(null);
  const [a, setA] = useState("python"), [b, setB] = useState("python programming");
  const [sim, setSim] = useState(null);

  useEffect(() => { const t = setTimeout(() => api.get("/matching/evaluation", { params: { k, ...w } }).then((r) => setEv(r.data)).catch(() => {}), 200); return () => clearTimeout(t); }, [w, k]);
  useEffect(() => { const t = setTimeout(() => api.get("/matching/similarity", { params: { a, b } }).then((r) => setSim(r.data)).catch(() => {}), 200); return () => clearTimeout(t); }, [a, b]);

  return (
    <div className="two">
      <section className="card"><h2>Tune the weights</h2>
        <p className="sub">The compatibility score blends five signals. Move a slider and the test on the right updates.</p>
        {W.map(([key, label]) => (
          <div className="wrow" key={key}><label htmlFor={"w-" + key}>{label}</label>
            <input type="range" id={"w-" + key} min="0" max="100" value={Math.round(w[key] * 100)} onChange={(e) => setW({ ...w, [key]: +e.target.value / 100 })} />
            <output>{Math.round(w[key] * 100)}</output></div>
        ))}
        <button className="btn ghost" onClick={() => setW(DEFAULTS)}>Back to default weights</button>
        <h3 className="subh">Try the skill similarity</h3>
        <p className="sub">TF-IDF over letter groups, compared with cosine similarity.</p>
        <div className="simrow"><input type="text" value={a} onChange={(e) => setA(e.target.value)} aria-label="First skill" /><input type="text" value={b} onChange={(e) => setB(e.target.value)} aria-label="Second skill" /></div>
        {sim && <p className="simout">Similarity <strong>{sim.score.toFixed(2)}</strong>. {sim.is_match ? "Counts as a match." : `Not a match (needs ${sim.threshold}).`}</p>}
      </section>
      <section className="card"><h2>Does it beat keyword search?</h2>
        <p className="sub">Tested on synthetic students. A peer counts as relevant when the swap works both ways.</p>
        <label className="field inline">Top K <select value={k} onChange={(e) => setK(+e.target.value)}>{[3, 5, 8].map((x) => <option key={x}>{x}</option>)}</select></label>
        {ev && (ev.students ? <><Bar label="SkillMesh matching" v={ev.skillmesh} cls="t" /><Bar label="Exact keyword search" v={ev.keyword} cls="a" /><p className="hint">Precision@{ev.k} over {ev.students} students</p></> : <p className="empty">Not enough students have {k} relevant peers. Try a smaller K.</p>)}
      </section>
    </div>
  );
}
