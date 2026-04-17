"use client";

import { useMemo, useState } from "react";
import { tokenStore } from "../../lib/auth";

export default function LoginPage() {
  const [username, setU] = useState("");
  const [password, setP] = useState("");
  const [show, setShow] = useState(false);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  const apiBase = useMemo(
    () => process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000",
    []
  );

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    setLoading(true);

    try {
      const res = await fetch(`${apiBase}/api/auth/token/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });

      if (!res.ok) {
        setErr("Логин немесе пароль қате. (Django admin user тексер)");
        return;
      }

      const data = await res.json();
      tokenStore.setTokens(data.access, data.refresh);
      location.href = "/";
    } catch {
      setErr("Серверге қосыла алмадым. Backend runserver қосулы ма?");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Top bar */}
      <div className="sticky top-0 bg-white/80 backdrop-blur border-b">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
          <a href="/" className="font-extrabold text-xl tracking-tight">
            Vid<span className="text-blue-600">Jobs</span>
          </a>
          <a
            href="/"
            className="text-sm text-slate-600 hover:text-slate-900"
          >
            ← Басты бет
          </a>
        </div>
      </div>

      {/* Center */}
      <div className="max-w-5xl mx-auto px-4 py-10">
        <div className="grid lg:grid-cols-2 gap-6 items-stretch">
          {/* Left promo */}
          <div className="rounded-3xl border bg-white p-6 shadow-sm">
            <div className="inline-flex items-center gap-2 rounded-full bg-blue-50 px-3 py-1 text-sm font-semibold text-blue-700">
              🔒 Қауіпсіз кіру (JWT)
            </div>

            <h1 className="mt-4 text-3xl font-extrabold leading-tight">
              Тапсырысты тез жарияла.
              <br />
              Орындаушыны оңай тап.
            </h1>

            <p className="mt-3 text-slate-600">
              VidJobs — видео/дауыс арқылы тапсырыс беріп, жүйе автоматты түрде
              техникалық тапсырма (ТЗ) жасайтын платформа.
            </p>

            <div className="mt-6 grid gap-3">
              <div className="rounded-2xl border bg-slate-50 p-4">
                <div className="font-bold">1) Кіру</div>
                <div className="text-sm text-slate-600">
                  Токен аласың → job жариялау ашылады.
                </div>
              </div>
              <div className="rounded-2xl border bg-slate-50 p-4">
                <div className="font-bold">2) Жариялау</div>
                <div className="text-sm text-slate-600">
                  Title/desc/budget → кейін video/voice қосамыз.
                </div>
              </div>
              <div className="rounded-2xl border bg-slate-50 p-4">
                <div className="font-bold">3) AI ТЗ</div>
                <div className="text-sm text-slate-600">
                  Whisper → GPT → Confirm → Publish (келесі кезең).
                </div>
              </div>
            </div>
          </div>

          {/* Right form */}
          <div className="rounded-3xl border bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-extrabold">Кіру</h2>
              <span className="text-xs text-slate-500">
                API: {apiBase.replace("http://", "")}
              </span>
            </div>

            <p className="mt-2 text-sm text-slate-600">
              Әзірге тест үшін Django admin қолданушысын қолданамыз.
            </p>

            <form onSubmit={onSubmit} className="mt-6 grid gap-3">
              <div className="grid gap-1">
                <label className="text-sm font-semibold text-slate-700">
                  Username
                </label>
                <input
                  className="w-full rounded-2xl border p-3 outline-none focus:ring-4 focus:ring-blue-100"
                  placeholder="admin"
                  value={username}
                  onChange={(e) => setU(e.target.value)}
                  autoComplete="username"
                />
              </div>

              <div className="grid gap-1">
                <label className="text-sm font-semibold text-slate-700">
                  Password
                </label>
                <div className="flex items-center gap-2 rounded-2xl border p-3 focus-within:ring-4 focus-within:ring-blue-100">
                  <input
                    className="w-full outline-none"
                    placeholder="••••••••"
                    type={show ? "text" : "password"}
                    value={password}
                    onChange={(e) => setP(e.target.value)}
                    autoComplete="current-password"
                  />
                  <button
                    type="button"
                    onClick={() => setShow((v) => !v)}
                    className="text-sm font-semibold text-slate-600 hover:text-slate-900"
                  >
                    {show ? "Жасыру" : "Көрсету"}
                  </button>
                </div>
              </div>

              {err && (
                <div className="rounded-2xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                  {err}
                </div>
              )}

              <button
                disabled={loading || !username.trim() || !password.trim()}
                className="mt-1 rounded-2xl bg-blue-600 p-3 font-extrabold text-white hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600"
              >
                {loading ? "Кіру..." : "Кіру"}
              </button>

              <div className="text-xs text-slate-500">
                Кіргеннен кейін басты бетте job жариялау жұмыс істейді.
              </div>
            </form>

            <div className="mt-6 rounded-2xl border bg-slate-50 p-4">
              <div className="text-sm font-bold">Егер кірмей жатса:</div>
              <ul className="mt-2 text-sm text-slate-600 list-disc pl-5 space-y-1">
                <li>Backend қосулы ма: <code>manage.py runserver</code></li>
                <li>Django admin user бар ма: <code>python manage.py createsuperuser</code></li>
                <li>CORS-та <code>http://localhost:3001</code> қосылған ба</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="mt-8 text-center text-xs text-slate-500">
          © VidJobs MVP — Web + Mobile бір backend арқылы
        </div>
      </div>
    </div>
  );
}