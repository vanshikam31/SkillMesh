import { useCallback, useEffect, useState } from "react";
import api, { errorText } from "../api";
import { useToast } from "../components/Toast";
import { slotLabel } from "../utils";

function Feedback({ session, onDone }) {
  const [stars, setStars] = useState(0);
  const [text, setText] = useState("");
  const toast = useToast();
  const submit = async () => {
    if (!stars) return toast("Choose a star rating first.");
    try {
      await api.post(`/sessions/${session.id}/rating`, { score: stars, feedback: text });
      toast(`Rating saved. It feeds ${session.peer.name}'s ranking for future matches.`); onDone();
    } catch (e) { toast(errorText(e)); }
  };
  return (
    <div className="rate">
      <p>Share your feedback for {session.peer.name}. How was the session?</p>
      <div className="stars">{[1, 2, 3, 4, 5].map((n) => <button key={n} className={"star" + (stars >= n ? " on" : "")} aria-label={`${n} star${n > 1 ? "s" : ""}`} onClick={() => setStars(n)}>&#9733;</button>)}</div>
      <textarea rows="2" placeholder="Optional feedback" value={text} onChange={(e) => setText(e.target.value)} />
      <button className="btn primary" onClick={submit}>Save rating</button>
    </div>
  );
}

export default function Sessions() {
  const [sessions, setSessions] = useState(null);
  const toast = useToast();
  const load = useCallback(() => api.get("/sessions").then((r) => setSessions(r.data)).catch((e) => toast(errorText(e))), [toast]);
  useEffect(() => { load(); }, [load]);
  const act = (req) => req.then(load).catch((e) => toast(errorText(e)));

  if (sessions === null) return <p className="empty">Loading sessions...</p>;
  if (!sessions.length) return <section className="card"><h2>Sessions</h2><p className="empty">Accept a request or send one from Discover. Connected peers appear here so you can pick a time.</p></section>;
  return (
    <div className="sess">
      {sessions.map((s) => (
        <section className="card" key={s.id}>
          <h2>{s.peer.name}</h2><p className="sub">{Math.round(s.score * 100)}% match</p>
          <ul className="why">{s.reasons.map((x) => <li key={x}>{x}</li>)}</ul>
          {s.my_rating ? <p>Session done. You rated {s.peer.name} {s.my_rating} out of 5.{s.feedback ? ` Your note: ${s.feedback}` : ""}</p>
            : s.completed ? <Feedback session={s} onDone={load} />
            : <>
              {s.shared_slots.length ? (
                <><p className="lbl">Pick a time you both have free</p>
                  <div className="slots">{s.shared_slots.map((k) => <button key={k} className="slotpick" aria-pressed={s.slot === k} onClick={() => act(api.put(`/sessions/${s.id}/schedule`, { slot: k }))}>{slotLabel(k)}</button>)}</div></>
              ) : <p className="empty">No shared free time yet. Add more slots to your profile.</p>}
              {s.slot && <div className="pact"><span className="tag accepted">Scheduled: {slotLabel(s.slot)}</span><button className="btn" onClick={() => act(api.post(`/sessions/${s.id}/complete`))}>Mark session as done</button></div>}
            </>}
        </section>
      ))}
    </div>
  );
}
