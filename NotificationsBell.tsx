"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { unreadCount } from "@/lib/api";

export default function NotificationsBell() {
  const [unread, setUnread] = useState<number>(0);

  async function load() {
    try {
      const data = await unreadCount(); // { unread: number }
      const n = Number(data?.unread ?? 0);
      setUnread(Number.isFinite(n) ? n : 0);
    } catch {
      // logged out болса 401 болуы мүмкін → просто 0 қыламыз
      setUnread(0);
    }
  }

  useEffect(() => {
    load();
    const t = setInterval(load, 9000);
    return () => clearInterval(t);
  }, []);

  return (
    <Link
      href="/me"
      className="relative rounded-xl border px-3 py-2 text-sm font-semibold hover:opacity-90"
      style={{ borderColor: "var(--border)", background: "var(--surface)" }}
      title="Notifications"
    >
      🔔
      {unread > 0 && (
        <span
          className="absolute -top-2 -right-2 min-w-[20px] h-[20px] px-1 rounded-full text-[11px] font-extrabold grid place-items-center"
          style={{ background: "var(--primary)", color: "white" }}
        >
          {unread > 99 ? "99+" : unread}
        </span>
      )}
    </Link>
  );
}