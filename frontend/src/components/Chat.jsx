import { useEffect, useRef, useState } from "react";
import api, { errorText } from "../api";
import { initials } from "../utils";
import { useToast } from "./Toast";

function stamp(iso) {
  const d = new Date(iso), time = d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  return d.toDateString() === new Date().toDateString() ? time : `${d.toLocaleDateString([], { day: "numeric", month: "short" })}, ${time}`;
}

/* One open conversation: header, message bubbles, input. Enter sends the message. */
export default function Chat({ session, onBack, onChanged }) {
  const sid = session.session_id, peer = session.peer;
  const [msgs, setMsgs] = useState([]);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const last = useRef(0);          // id of the newest message we already have
  const log = useRef(null);
  const toast = useToast();

  const markRead = async () => {
    try { const { data } = await api.post(`/sessions/${sid}/read`); if (data.marked) onChanged?.(); } catch { /* ignore */ }
  };
  const load = async () => {
    try {
      const { data } = await api.get(`/sessions/${sid}/messages`, { params: { after: last.current } });
      if (data.length) {
        last.current = data[data.length - 1].id;
        setMsgs((m) => [...m, ...data]);
        if (data.some((m) => !m.mine)) markRead();        // the other person's messages are now read
      }
    } catch { /* keep the old messages if the network blinks */ }
  };
  useEffect(() => { load(); const t = setInterval(load, 3000); return () => clearInterval(t); }, [sid]);        // eslint-disable-line
  useEffect(() => { if (log.current) log.current.scrollTop = log.current.scrollHeight; }, [msgs]);

  const send = async (e) => {
    e.preventDefault();
    const v = text.trim();
    if (!v) return;
    setBusy(true);
    try { await api.post(`/sessions/${sid}/messages`, { text: v }); setText(""); await load(); onChanged?.(); }
    catch (ex) { toast(errorText(ex)); } finally { setBusy(false); }
  };

  return (
    <div className="chat">
      <header className="chathead">
        <button className="btn small backbtn" onClick={onBack} aria-label="Back to conversations">Back</button>
        <span className="pico sm">{initials(peer.name)}</span>
        <div><strong>{peer.name}</strong><p className="sub" style={{ margin: 0 }}>Skill exchange partner</p></div>
        <a className="btn small" href="https://meet.new" target="_blank" rel="noopener noreferrer" style={{ marginLeft: "auto" }}>Start video call</a>
      </header>
      <div className="chatlog" ref={log} role="log" aria-live="polite" aria-label={`Chat with ${peer.name}`}>
        {msgs.length === 0 && <p className="empty">No messages yet. Say hello to {peer.name} and agree on a time.</p>}
        {msgs.map((m) => (
          <div key={m.id} className={"bubble" + (m.mine ? " mine" : "")}>
            <b className="who">{m.mine ? "You" : m.sender_name}</b>
            <span>{m.text}</span>
            <small>{stamp(m.created_at)}</small>
          </div>
        ))}
      </div>
      <form className="chatform" onSubmit={send}>
        <textarea rows="1" value={text} onChange={(e) => setText(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); e.currentTarget.form.requestSubmit(); } }} placeholder="Type a message (Enter to send, Shift + Enter for a new line)" maxLength={1000} aria-label="Message" autoFocus />
        <button className="btn primary small" type="submit" disabled={busy}>Send</button>
      </form>
    </div>
  );
}
