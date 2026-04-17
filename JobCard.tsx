"use client";

import JobActions from "./JobActions";
import Link from "next/link";

type Job = {
  id: number;
  title: string;
  description: string;
  category: string;
  budget: number;
  created_at: string;
  owner_username?: string;
  status?: "published" | "assigned" | "done";
  assigned_to?: number | null;
};

const catLabel: Record<string, string> = {
  repair: "🔧 Жөндеу",
  cleaning: "🧹 Тазалау",
  delivery: "📦 Жеткізу",
  heavy: "🚜 Ауыр жұмыс",
};

const statusLabel: Record<string, string> = {
  published: "Жарияланды",
  assigned: "Орындаушы таңдалды",
  done: "Аяқталды",
};

function statusBg(status: Job["status"]) {
  if (status === "done") return "rgba(34,197,94,0.12)";
  if (status === "assigned") return "rgba(59,130,246,0.12)";
  return "rgba(148,163,184,0.12)";
}

export default function JobCard({
  job,
  mode = "feed",
  onChanged,
}: {
  job: Job;
  mode?: "feed" | "owner" | "executor";
  onChanged?: () => void;
}) {
  const date = new Date(job.created_at);
  const dateStr = isNaN(date.getTime()) ? "—" : date.toLocaleDateString("kk-KZ");

  const s: Job["status"] = job.status ?? "published";

  return (
    <div
      className="rounded-[24px] border p-5 shadow-sm hover:-translate-y-1 hover:shadow-md active:scale-[0.995] transition"
      style={{ background: "var(--surface)", borderColor: "var(--border)" }}
    >
      {/* Top row */}
      <div className="flex items-start justify-between gap-3">
        <div className="text-xl font-extrabold" style={{ color: "var(--primary)" }}>
          {job.budget?.toLocaleString?.("ru-RU") ?? job.budget} ₸
        </div>

        <div className="flex items-center gap-2">
          {/* ✅ STATUS BADGE (label) */}
          <span
            className="rounded-full border px-3 py-1 text-xs font-semibold"
            style={{
              background: statusBg(s),
              borderColor: "var(--border)",
              color: "var(--muted)",
            }}
          >
            {statusLabel[s] ?? s}
          </span>

          {/* CATEGORY BADGE */}
          <span
            className="rounded-full border px-3 py-1 text-xs font-semibold"
            style={{
              background: "var(--surface-2)",
              borderColor: "var(--border)",
              color: "var(--muted)",
            }}
          >
            {catLabel[job.category] ?? job.category}
          </span>
        </div>
      </div>

      {/* Title */}
      <Link href={`/jobs/${job.id}`} className="mt-3 block text-lg font-extrabold tracking-tight hover:underline">
        {job.title || "—"}
      </Link>

      {/* Desc */}
      <p className="mt-2 text-sm leading-relaxed" style={{ color: "var(--muted)" }}>
        {job.description || "—"}
      </p>

      {/* ✅ ACTIONS (көзге көрінетін үлкен нәрсе осы) */}
      <JobActions
        mode={mode}
        jobId={job.id}
        status={s}
        assignedTo={job.assigned_to ?? null}
        onChanged={onChanged}
      />

      {/* Bottom row */}
      <div className="mt-5 flex items-center justify-between text-xs">
        <span style={{ color: "var(--muted)" }}>{job.owner_username ? job.owner_username : "—"}</span>
        <span style={{ color: "var(--muted)" }}>{dateStr}</span>
      </div>
    </div>
  );
}