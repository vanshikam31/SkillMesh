import { useState } from "react";

export default function SkillInput({ label, skills, onChange, suggestions = [], listId }) {
  const [text, setText] = useState("");
  const add = () => {
    const v = text.trim();
    if (v && !skills.some((s) => s.toLowerCase() === v.toLowerCase())) onChange([...skills, v]);
    setText("");
  };
  return (
    <div className="field">
      <span className="lbl">{label}</span>
      <div className="chips">
        {skills.map((s) => (
          <span className="chip" key={s}>{s}
            <button type="button" aria-label={`Remove ${s}`} onClick={() => onChange(skills.filter((x) => x !== s))}>&times;</button>
          </span>
        ))}
      </div>
      <div className="addrow">
        <input type="text" list={listId} value={text} placeholder="Type a skill, press Enter" aria-label={label}
          onChange={(e) => setText(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); add(); } }} />
        <button type="button" className="btn small" onClick={add}>Add</button>
      </div>
      <datalist id={listId}>{suggestions.map((s) => <option key={s} value={s} />)}</datalist>
    </div>
  );
}
