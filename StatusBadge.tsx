"use client";

export default function StatusBadge({ status }: { status: "published" | "assigned" | "done" }) {
  const label =
    status === "done" ? "Аяқталды" : status === "assigned" ? "Орындаушы таңдалды" : "Жарияланды";

  const bg =
    status === "done"
      ? "rgba(34,197,94,0.12)"
      : status === "assigned"
      ? "rgba(59,130,246,0.12)"
      : "rgba(148,163,184,0.12)";

  return (
    <span
      className="rounded-full border px-3 py-1 text-xs font-semibold"
      style={{ background: bg, borderColor: "var(--border)", color: "var(--muted)" }}
      title={label}
    >
      {label}
    </span>
  );
}