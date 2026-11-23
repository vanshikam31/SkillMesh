import { Link } from "react-router-dom";
import { EXP, PARTS, initials } from "../utils";

/* A row of skill tags. Tags listed in `hits` are highlighted (they match something on the other side). */
function Chips({ label, skills, hits = [], empty = "None" }) {
  return (
    <div className="skillrow">
      <span className="rowlabel">{label}</span>
      <span className="chiplist">
        {skills.length
          ? skills.map((s) => <span key={s} className={"chip sm" + (hits.includes(s) ? " hit" : "")}>{s}</span>)
          : <span className="note">{empty}</span>}
      </span>
    </div>
  );
}

export default function PeerCard({ match, selected, onSend }) {
  const p = match.peer, pct = Math.round(match.score * 100), st = match.request_status;
  let action;
  if (!st) action = <button className="btn primary" onClick={() => onSend(p)}>Send request</button>;
  else if (st === "pending_out") action = <button className="btn" disabled>Request pending</button>;
  else if (st === "pending_in") action = <Link className="btn" to="/requests">Reply to their request</Link>;
  else if (st === "accepted") action = <Link className="btn" to={`/sessions?chat=${match.session_id}`}>Open chat</Link>;
  else action = <span className="note">Request rejected</span>;

  return (
    <article className={"peer" + (selected ? " sel" : "")} id={"peer-" + p.id}>
      <div className="pico">{initials(p.name)}</div>
      <div className="pbody">
        <div className="phead">
          <div>
            <h3>{p.name}{p.is_sample && <span className="tag" style={{ marginLeft: 8, fontSize: ".75rem" }}>Sample</span>}</h3>
            <p className="sub">{EXP[p.experience]}. Rated {p.rating.toFixed(1)} from {p.rating_count} sessions</p>
          </div>
          <div className="pct" aria-label={`${pct} percent match`}><strong>{pct}%</strong><span>match</span></div>
        </div>

        {match.mutual ? (
          <>
            <Chips label="You can learn" skills={match.learn} hits={match.learn} />
            <Chips label="You can teach" skills={match.teach} hits={match.teach} />
            <details>
              <summary>Everything they offer and want</summary>
              <Chips label="They offer" skills={p.offered} hits={match.learn} />
              <Chips label="They want" skills={p.wanted} hits={match.teach} />
            </details>
          </>
        ) : (
          <>
            <Chips label="They offer (you can learn)" skills={p.offered} hits={match.learn} empty="Nothing listed" />
            <Chips label="They want (you could teach)" skills={p.wanted} hits={match.teach} empty="Nothing listed" />
            <p className="hint">{match.learn.length || match.teach.length
              ? "Highlighted skills match your profile."
              : "No direct match with your skills yet, but you may find something new to learn."}</p>
          </>
        )}

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
