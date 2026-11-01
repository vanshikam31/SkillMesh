export const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
export const SLOTS = [["M", "morning"], ["A", "afternoon"], ["E", "evening"]];
export const EXP = ["", "Beginner", "Basic", "Intermediate", "Advanced", "Expert"];
export const PARTS = [
  ["skill", "Teaches what you want"], ["reverse", "Wants what you offer"], ["exp", "Experience fit"],
  ["avail", "Shared free time"], ["rating", "Peer rating"],
];
export const initials = (n = "") => n.split(" ").map((x) => x[0]).slice(0, 2).join("").toUpperCase();
export const slotLabel = (k) => { const [d, s] = k.split("-"); return `${d} ${SLOTS.find((x) => x[0] === s)[1]}`; };
