export default function Logo({ className = "" }) {
  return (
    <svg className={className} viewBox="0 0 40 40" aria-hidden="true">
      <g stroke="currentColor" strokeWidth="2" fill="none" opacity=".55">
        <line x1="20" y1="20" x2="6" y2="9" /><line x1="20" y1="20" x2="34" y2="9" />
        <line x1="20" y1="20" x2="8" y2="33" /><line x1="20" y1="20" x2="33" y2="31" /><line x1="6" y1="9" x2="34" y2="9" />
      </g>
      <circle cx="20" cy="20" r="6" className="lg-c" />
      {[[6, 9], [34, 9], [8, 33], [33, 31]].map(([x, y]) => <circle key={x + "-" + y} cx={x} cy={y} r="3.5" className="lg-n" />)}
    </svg>
  );
}
