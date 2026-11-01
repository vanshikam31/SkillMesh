import { initials } from "../utils";

export default function MeshGraph({ matches, selected, onSelect }) {
  const top = matches.slice(0, 8), cx = 260, cy = 195, rx = 205, ry = 140;
  const nodes = top.map((m, i) => {
    const a = -Math.PI / 2 + (i * 2 * Math.PI) / top.length;
    return { m, x: cx + rx * Math.cos(a), y: cy + ry * Math.sin(a) };
  });
  return (
    <svg viewBox="0 0 520 400" role="img" aria-label="Your top matches around you. Thicker lines mean stronger matches.">
      {nodes.map((n, i) => { const o = nodes[(i + 1) % nodes.length]; return <line key={"r" + i} x1={n.x} y1={n.y} x2={o.x} y2={o.y} className="ringline" />; })}
      {nodes.map((n) => (
        <line key={"s" + n.m.peer.id} x1={cx} y1={cy} x2={n.x} y2={n.y} className={"spoke" + (selected === n.m.peer.id ? " on" : "")} strokeWidth={(1.5 + n.m.score * 10).toFixed(1)} />
      ))}
      {nodes.map((n) => {
        const p = n.m.peer, connected = n.m.request_status === "accepted";
        return (
          <g key={p.id} className={"node" + (selected === p.id ? " sel" : "") + (connected ? " conn" : "")} tabIndex={0} role="button"
            aria-label={`${p.name}, ${Math.round(n.m.score * 100)} percent match`} onClick={() => onSelect(p.id)}
            onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); onSelect(p.id); } }}>
            <circle cx={n.x} cy={n.y} r="25" />
            <text x={n.x} y={n.y + 5} className="ni">{initials(p.name)}</text>
            <text x={n.x} y={n.y + 42} className="nm">{Math.round(n.m.score * 100)}%</text>
          </g>
        );
      })}
      <circle cx={cx} cy={cy} r="34" className="me" />
      <text x={cx} y={cy + 5} className="mt">You</text>
    </svg>
  );
}
