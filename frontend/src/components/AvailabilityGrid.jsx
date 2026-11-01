import { DAYS, SLOTS } from "../utils";

export default function AvailabilityGrid({ value, onChange }) {
  const toggle = (k) => onChange(value.includes(k) ? value.filter((x) => x !== k) : [...value, k]);
  return (
    <div className="field">
      <span className="lbl">Free time (tap to toggle)</span>
      <div className="grid" role="group" aria-label="Weekly availability">
        <span />{SLOTS.map((s) => <span className="gh" key={s[0]} title={s[1]}>{s[0]}</span>)}
        {DAYS.map((d) => (
          <span key={d} style={{ display: "contents" }}>
            <span className="gd">{d}</span>
            {SLOTS.map((s) => {
              const k = `${d}-${s[0]}`;
              return <button type="button" key={k} className="slot" aria-pressed={value.includes(k)} aria-label={`${d} ${s[1]}`} onClick={() => toggle(k)} />;
            })}
          </span>
        ))}
      </div>
      <p className="hint">M morning, A afternoon, E evening</p>
    </div>
  );
}
