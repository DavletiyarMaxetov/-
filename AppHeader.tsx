"use client";

import { useEffect, useState } from "react";
import ThemeToggle from "./ThemeToggle";
import NotificationsBell from "./NotificationsBell";
import { apiFetch } from "@/lib/api";
import Link from "next/link";
import { tokenStore } from "@/lib/auth";

export default function AppHeader() {
  const [me, setMe] = useState<any>(null);

  async function loadMe() {
    try {
      const p = await apiFetch("/api/me/");
      setMe(p);
    } catch {
      setMe(null);
    }
  }

  useEffect(() => {
    loadMe();
  }, []);

  function logout() {
    // tokenStore-да сен қалай сақтайсың — солай тазалау керек
    tokenStore.setTokens("", ""); // егер setTokens бар болса
    // егер жоқ болса:
    // localStorage.removeItem("access");
    // localStorage.removeItem("refresh");
    location.href = "/";
  }

  return (
    <header
      className="sticky top-0 z-20 border-b backdrop-blur"
      style={{
        background: "color-mix(in oklab, var(--surface) 80%, transparent)",
        borderColor: "var(--border)",
      }}
    >
      <div className="mx-auto max-w-6xl px-4 py-3 flex items-center justify-between gap-3">
        <Link href="/" className="flex items-center gap-3">
          <div
            className="h-10 w-10 rounded-2xl grid place-items-center font-extrabold text-white"
            style={{ background: "var(--primary)" }}
          >
            V
          </div>
          <div className="leading-tight">
            <div className="text-lg font-extrabold tracking-tight">
              Vid<span style={{ color: "var(--primary)" }}>Jobs</span>
            </div>
            <div className="text-xs" style={{ color: "var(--muted)" }}>
              Minimal Premium Web
            </div>
          </div>
        </Link>

        <div className="flex items-center gap-2">
          <NotificationsBell />
          <ThemeToggle />

          {me ? (
            <>
              <Link
                href="/me"
                className="rounded-xl border px-4 py-2 text-sm font-semibold hover:opacity-90"
                style={{ borderColor: "var(--border)", background: "var(--surface)" }}
              >
                My
              </Link>

              <div
                className="rounded-xl border px-3 py-2 text-sm font-semibold"
                style={{ borderColor: "var(--border)", background: "var(--surface)" }}
                title={`role: ${me.role}`}
              >
                @{me.username}
              </div>

              <button
                onClick={logout}
                className="rounded-xl border px-3 py-2 text-sm font-semibold hover:opacity-90"
                style={{ borderColor: "var(--border)", background: "var(--surface)" }}
              >
                Logout
              </button>
            </>
          ) : (
            <a
              href="/login"
              className="rounded-xl border px-4 py-2 text-sm font-semibold hover:opacity-90"
              style={{ borderColor: "var(--border)", background: "var(--surface)" }}
            >
              Login
            </a>
          )}
        </div>
      </div>
    </header>
  );
}