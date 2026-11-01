import { Link } from "react-router-dom";
import { initials } from "../utils";

function Row({ r, onRespond }) {
  return (
    <div className="row">
      <div className="pico sm">{initials(r.peer.name)}</div>
      <div className="rbody">
        <strong>{r.peer.name}</strong> <span className="sub">{Math.round(r.score * 100)}% match</span>
        <ul className="why">{r.reasons.slice(0, 2).map((x) => <li key={x}>{x}</li>)}</ul>
      </div>
      <div className="ract">
        {r.direction === "in" && r.status === "pending" ? (
          <>
            <button className="btn primary small" onClick={() => onRespond(r.id, "accept")}>Accept</button>
            <button className="btn small" onClick={() => onRespond(r.id, "decline")}>Decline</button>
          </>
        ) : <span className={"tag " + r.status}>{r.status === "pending" ? "Waiting" : r.status === "accepted" ? "Accepted" : "Declined"}</span>}
      </div>
    </div>
  );
}

export default function Requests({ requests, onRespond }) {
  const inc = requests.filter((r) => r.direction === "in"), out = requests.filter((r) => r.direction === "out");
  return (
    <div className="two">
      <section className="card"><h2>Requests to you</h2>
        {inc.length ? inc.map((r) => <Row key={r.id} r={r} onRespond={onRespond} />) : <p className="empty">Nobody has asked yet.</p>}
      </section>
      <section className="card"><h2>Requests you sent</h2>
        {out.length ? out.map((r) => <Row key={r.id} r={r} onRespond={onRespond} />) : <p className="empty">Send a request from <Link to="/discover">Discover</Link> and the reply shows up here.</p>}
      </section>
    </div>
  );
}
