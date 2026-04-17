"use client";

import { useEffect, useState } from "react";

export default function ThemeToggle() {
  const [theme, setTheme] = useState<"light" | "dark">("light");

  useEffect(() => {
    const saved = (localStorage.getItem("theme") as "light" | "dark" | null) ?? null;
    const prefersDark = window.matchMedia?.("(prefers-color-scheme: dark)")?.matches;
    const initial = saved ?? (prefersDark ? "dark" : "light");
    setTheme(initial);
    document.documentElement.dataset.theme = initial;
  }, []);

  function toggle() {
    const next = theme === "light" ? "dark" : "light";
    setTheme(next);
    document.documentElement.dataset.theme = next;
    localStorage.setItem("theme", next);
  }

  return (
    <button
      onClick={toggle}
      className="rounded-xl border px-3 py-2 text-sm font-semibold hover:opacity-90"
      style={{ borderColor: "var(--border)", background: "var(--surface)" }}
      aria-label="Theme toggle"
      title="Theme"
    >
      {theme === "light" ? "🌙" : "☀️"}
    </button>
  );
}