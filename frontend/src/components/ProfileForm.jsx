import { useEffect, useState } from "react";
import api from "../api";
import { EXP } from "../utils";
import AvailabilityGrid from "./AvailabilityGrid";
import SkillInput from "./SkillInput";

export default function ProfileForm({ user, onSave, saving, buttonText, title }) {
  const [form, setForm] = useState({ name: user.name, experience: user.experience, offered: user.offered, wanted: user.wanted, availability: user.availability, bio: user.bio || "" });
  const [suggestions, setSuggestions] = useState([]);
  useEffect(() => { api.get("/skills").then((r) => setSuggestions(r.data)).catch(() => {}); }, []);
  const set = (k) => (v) => setForm((f) => ({ ...f, [k]: v }));

  return (
    <>
      {title && <h2>{title}</h2>}
      <label className="field">Name
        <input type="text" value={form.name} onChange={(e) => set("name")(e.target.value)} />
      </label>
      <label className="field">Experience level
        <select value={form.experience} onChange={(e) => set("experience")(+e.target.value)}>
          {[1, 2, 3, 4, 5].map((i) => <option key={i} value={i}>{EXP[i]}</option>)}
        </select>
      </label>
      <SkillInput label="Skills you can teach" skills={form.offered} onChange={set("offered")} suggestions={suggestions} listId={"o-" + (title || "p")} />
      <SkillInput label="Skills you want to learn" skills={form.wanted} onChange={set("wanted")} suggestions={suggestions} listId={"w-" + (title || "p")} />
      <AvailabilityGrid value={form.availability} onChange={set("availability")} />
      <button className="btn primary wide" disabled={saving} onClick={() => onSave(form)}>{buttonText}</button>
    </>
  );
}
