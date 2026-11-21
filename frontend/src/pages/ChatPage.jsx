import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import ChatCenter from "../components/ChatCenter";

/** Dedicated inbox page for accepted SkillMesh connections. */
export default function ChatPage() {
  const [params] = useSearchParams();
  const requestedId = Number(params.get("session")) || null;
  const [active, setActive] = useState(requestedId);
  return (
    <section className="chatpage">
      <div className="chatpage-head">
        <div>
          <h1>Messages</h1>
          <p className="sub">Chat privately with students whose connection requests have been accepted.</p>
        </div>
      </div>
      <ChatCenter activeId={active} onSelect={setActive} />
    </section>
  );
}
