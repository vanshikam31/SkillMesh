import { Link } from "react-router-dom";
import { EXP, PARTS, initials } from "../utils";

export default function PeerCard({ match, selected, onSend }) {
  const p = match.peer, pct = Math.round(match.score * 100), st = match.request_status;
  let action;
  if (!st) action = <button className="btn primary" onClick={() => onSend(p)}>Send request</button>;
  else if (st === "pending_out") action = <button className="btn" disabled>Waiting for a reply</button>;
  else if (st === "pending_in") action = <Link className="btn" to="/requests">Reply to their request</Link>;
  else if (st === "accepted") action = <Link className="btn" to="/sessions">Plan a session</Link>;
  else action = <span className="note">Request declined</span>;
  return (
    <article className={"peer" + (selected ? " sel" : "")} id={"peer-" + p.id}>
      <div className="pico">{initials(p.name)}</div>
      <div className="pbody">
        <div className="phead">
          <div><h3>{p.name}</h3><p className="sub">{EXP[p.experience]}. Rated {p.rating.toFixed(1)} from {p.rating_count} sessions</p></div>
          <div className="pct" aria-label={`${pct} percent match`}><strong>{pct}%</strong><span>match</span></div>
        </div>
        <ul className="why">{match.reasons.map((r) => <li key={r}>{r}</li>)}</ul>
        <details>
          <summary>See how this score is built</summary>
          <div className="meters">
            {PARTS.map(([k, label]) => (
              <div className="meter" key={k}><span>{label}</span><i style={{ "--v": `${Math.round(match.parts[k] * 100)}%` }} /><b>{Math.round(match.parts[k] * 100)}</b></div>
            ))}
          </div>
        </details>
        <div className="pact">{action}</div>
      </div>
    </article>
  );
}
