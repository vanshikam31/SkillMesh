import { Link } from "react-router-dom";
import { initials } from "../utils";

const LABEL = { pending: "Pending", accepted: "Accepted", declined: "Rejected" };

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
            <button className="btn small" onClick={() => onRespond(r.id, "reject")}>Reject</button>
          </>
        ) : (
          <>
            <span className={"tag " + r.status}>{LABEL[r.status] || r.status}</span>
            {r.status === "accepted" && r.session_id && <Link className="btn small" to={`/sessions?chat=${r.session_id}`}>Open chat</Link>}
          </>
        )}
      </div>
    </div>
  );
}

export default function Requests({ requests, onRespond }) {
  const inc = requests.filter((r) => r.direction === "in"), out = requests.filter((r) => r.direction === "out");
  return (
    <div className="two">
      <section className="card"><h2>Received Requests</h2>
        {inc.length ? inc.map((r) => <Row key={r.id} r={r} onRespond={onRespond} />) : <p className="empty">No requests received yet.</p>}
      </section>
      <section className="card"><h2>Sent Requests</h2>
        {out.length ? out.map((r) => <Row key={r.id} r={r} onRespond={onRespond} />) : <p className="empty">Send a request from <Link to="/discover">Discover</Link> and its status shows up here.</p>}
      </section>
    </div>
  );
}
