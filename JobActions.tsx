"use client";

import { useState } from "react";
import { assignPerformer, markDone } from "@/lib/api";

export default function JobActions({
  mode,
  jobId,
  status,
  assignedTo,
  onChanged,
}: {
  mode: "feed" | "owner" | "executor";
  jobId: number;
  status: "published" | "assigned" | "done";
  assignedTo: number | null;
  onChanged?: () => void;
}) {
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  async function onAssign() {
    const pid = prompt("performer_id енгіз:");
    if (!pid) return;

    setBusy(true);
    setErr("");
    try {
      await assignPerformer(jobId, Number(pid));
      onChanged?.();
    } catch (e: any) {
      setErr(e?.message || "Assign error");
    } finally {
      setBusy(false);
    }
  }

  async function onMarkDone() {
    setBusy(true);
    setErr("");
    try {
      await markDone(jobId);
      onChanged?.();
    } catch (e: any) {
      setErr(e?.message || "Mark done error");
    } finally {
      setBusy(false);
    }
  }

  const showAssign = mode === "owner" && status === "published";
  const showMarkDone = mode === "executor" && status === "assigned" && Boolean(assignedTo);

  if (!showAssign && !showMarkDone) return null;

  return (
    <div className="mt-4">
      {err && (
        <div className="mb-2 rounded-xl border border-red-500/20 bg-red-500/10 px-3 py-2 text-xs text-red-200">
          {err}
        </div>
      )}

      <div className="flex flex-wrap gap-2">
        {showAssign && (
          <button
            disabled={busy}
            onClick={onAssign}
            className="rounded-xl px-3 py-2 text-xs font-extrabold text-white disabled:opacity-50"
            style={{ background: "var(--primary)" }}
          >
            Assign
          </button>
        )}

        {showMarkDone && (
          <button
            disabled={busy}
            onClick={onMarkDone}
            className="rounded-xl border px-3 py-2 text-xs font-extrabold disabled:opacity-50"
            style={{ borderColor: "var(--border)", background: "var(--surface)" }}
          >
            Mark done
          </button>
        )}
      </div>
    </div>
  );
}