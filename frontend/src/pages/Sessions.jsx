import { useCallback, useEffect, useState } from "react";
import api, { errorText } from "../api";
import { useSearchParams } from "react-router-dom";
import ChatCenter from "../components/ChatCenter";
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
  const [params] = useSearchParams();
  const fromLink = Number(params.get("chat")) || null;           // /sessions?chat=ID opens that conversation
  const [tab, setTab] = useState(fromLink ? "chat" : "sessions");
  const [active, setActive] = useState(fromLink);
  const toast = useToast();
  const load = useCallback(() => api.get("/sessions").then((r) => setSessions(r.data)).catch((e) => toast(errorText(e))), [toast]);
  useEffect(() => { load(); }, [load]);
  const act = (req) => req.then(load).catch((e) => toast(errorText(e)));
  const openChat = (id) => { setActive(id); setTab("chat"); };

  const tabs = (
    <div className="seg subtabs" role="tablist" aria-label="Sessions sections">
      <button role="tab" aria-selected={tab === "sessions"} aria-pressed={tab === "sessions"} onClick={() => setTab("sessions")}>My Sessions</button>
      <button role="tab" aria-selected={tab === "chat"} aria-pressed={tab === "chat"} onClick={() => setTab("chat")}>Chat</button>
    </div>
  );
  if (tab === "chat") return <>{tabs}<ChatCenter activeId={active} onSelect={setActive} /></>;
  if (sessions === null) return <>{tabs}<p className="empty">Loading sessions...</p></>;
  if (!sessions.length) return <>{tabs}<section className="card"><h2>My Sessions</h2><p className="empty">Accept a request or send one from Discover. Accepted connections appear here so you can chat and pick a time.</p></section></>;
  return (
    <>{tabs}
    <div className="sess">
      {sessions.map((s) => (
        <section className="card" key={s.id}>
          <h2>{s.peer.name}</h2><p className="sub">{Math.round(s.score * 100)}% match</p>
          <ul className="why">{s.reasons.map((x) => <li key={x}>{x}</li>)}</ul>
          <div className="pact">
            <button className="btn small" onClick={() => openChat(s.id)}>{s.my_rating ? "Continue chat" : "Open chat"}</button>
            {s.slot && !s.completed && <a className="btn small" href="https://meet.new" target="_blank" rel="noopener noreferrer">Start video call</a>}
          </div>
          {s.slot && !s.completed && <p className="hint">The video call opens Google Meet. Copy the meeting link and paste it in the chat.</p>}
          {s.my_rating ? <p style={{ marginTop: 12 }}>Session done. You rated {s.peer.name} {s.my_rating} out of 5.{s.feedback ? ` Your note: ${s.feedback}` : ""} You can keep chatting in the Chat tab.</p>
            : s.completed ? <Feedback session={s} onDone={load} />
            : <>
              {s.shared_slots.length ? (
                <><p className="lbl" style={{ marginTop: 14 }}>Pick a time you both have free</p>
                  <div className="slots">{s.shared_slots.map((k) => <button key={k} className="slotpick" aria-pressed={s.slot === k} onClick={() => act(api.put(`/sessions/${s.id}/schedule`, { slot: k }))}>{slotLabel(k)}</button>)}</div></>
              ) : <p className="empty">No shared free time yet. Add more slots to your profile.</p>}
              {s.slot && <div className="pact"><span className="tag accepted">Scheduled: {slotLabel(s.slot)}</span><button className="btn" onClick={() => act(api.post(`/sessions/${s.id}/complete`))}>Mark session as done</button></div>}
            </>}
        </section>
      ))}
    </div>
    </>
  );
}
