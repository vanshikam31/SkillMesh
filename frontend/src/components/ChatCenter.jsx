import { useCallback, useEffect, useState } from "react";
import api from "../api";
import { initials } from "../utils";
import Chat from "./Chat";

/* Conversation list on the left (all accepted connections), the open conversation on the right. */
export default function ChatCenter({ activeId, onSelect }) {
  const [convs, setConvs] = useState(null);
  const [query, setQuery] = useState("");
  const load = useCallback(() => api.get("/sessions/conversations").then((r) => setConvs(r.data)).catch(() => {}), []);
  useEffect(() => { load(); const t = setInterval(load, 5000); return () => clearInterval(t); }, [load]);    // latest message and unread counts

  if (convs === null) return <p className="empty">Loading chats...</p>;
  if (!convs.length) return (
    <section className="card"><h2>Chat</h2>
      <p className="empty">No conversations yet. When a connection request is accepted, you can chat here.</p>
    </section>
  );
  const active = convs.find((c) => c.session_id === activeId);
  const visible = convs.filter((c) => c.peer.name.toLowerCase().includes(query.trim().toLowerCase()));
  return (
    <div className={"chatcenter" + (active ? " has-active" : "")}>
      <aside className="convlist" aria-label="Conversations">
        <div className="conv-search">
          <input type="search" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search conversations" aria-label="Search conversations" />
        </div>
        {visible.length === 0 ? <p className="empty conv-empty">No conversations match your search.</p> : visible.map((c) => (
          <button key={c.session_id} className={"conv" + (c.session_id === activeId ? " on" : "")} onClick={() => onSelect(c.session_id)}>
            <span className="pico sm">{initials(c.peer.name)}</span>
            <span className="convtext">
              <strong>{c.peer.name}</strong>
              <span className="preview">{c.last_message ? (c.last_mine ? "You: " : "") + c.last_message : "No messages yet"}</span>
            </span>
            {c.unread > 0 && <span className="badge" aria-label={`${c.unread} unread messages`}>{c.unread}</span>}
          </button>
        ))}
      </aside>
      <section className="convwin">
        {active ? <Chat key={active.session_id} session={active} onBack={() => onSelect(null)} onChanged={load} />
          : <p className="empty pad">Select a conversation to start chatting.</p>}
      </section>
    </div>
  );
}
