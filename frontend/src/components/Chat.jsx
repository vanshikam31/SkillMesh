import { useEffect, useRef, useState } from "react";
import api, { errorText } from "../api";
import { useToast } from "./Toast";

export default function Chat({ sessionId, peerName }) {
  const [msgs, setMsgs] = useState([]);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const last = useRef(0);          // id of the newest message we already have
  const log = useRef(null);
  const toast = useToast();

  const load = async () => {
    try {
      const { data } = await api.get(`/sessions/${sessionId}/messages`, { params: { after: last.current } });
      if (data.length) { last.current = data[data.length - 1].id; setMsgs((m) => [...m, ...data]); }
    } catch { /* keep the old messages if the network blinks */ }
  };
  useEffect(() => { load(); const t = setInterval(load, 4000); return () => clearInterval(t); }, [sessionId]);   // check for new messages every 4 seconds
  useEffect(() => { if (log.current) log.current.scrollTop = log.current.scrollHeight; }, [msgs]);

  const send = async (e) => {
    e.preventDefault();
    const v = text.trim();
    if (!v) return;
    setBusy(true);
    try { await api.post(`/sessions/${sessionId}/messages`, { text: v }); setText(""); await load(); }
    catch (ex) { toast(errorText(ex)); } finally { setBusy(false); }
  };
  const time = (iso) => new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  return (
    <div className="chat">
      <div className="chatlog" ref={log} role="log" aria-live="polite" aria-label={`Chat with ${peerName}`}>
        {msgs.length === 0 && <p className="empty">Say hello to {peerName} and agree on a time.</p>}
        {msgs.map((m) => (
          <div key={m.id} className={"bubble" + (m.mine ? " mine" : "")}>
            <span>{m.text}</span><small>{time(m.created_at)}</small>
          </div>
        ))}
      </div>
      <form className="chatform" onSubmit={send}>
        <input type="text" value={text} onChange={(e) => setText(e.target.value)} placeholder="Type a message" maxLength={1000} aria-label="Message" />
        <button className="btn primary small" type="submit" disabled={busy}>Send</button>
      </form>
    </div>
  );
}
