import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../AuthContext";
import Logo from "./Logo";

const links = [["/discover", "Discover"], ["/requests", "Requests"], ["/sessions", "Sessions"], ["/how-it-works", "How matching works"]];

export default function Navbar({ pending = 0 }) {
  const { logout } = useAuth();
  const nav = useNavigate();
  return (
    <header className="top">
      <div className="brand"><Logo />SkillMesh</div>
      <nav id="tabs" aria-label="Main">
        {links.map(([to, label]) => (
          <NavLink key={to} to={to} className="tab">{label}{to === "/requests" && pending ? ` (${pending})` : ""}</NavLink>
        ))}
        <button className="tab" onClick={() => { logout(); nav("/"); }}>Log out</button>
      </nav>
    </header>
  );
}
