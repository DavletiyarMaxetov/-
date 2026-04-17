// frontend/auth.ts
"use client";

const ACCESS_KEY = "access";
const REFRESH_KEY = "refresh";

function hasWindow() {
  return typeof window !== "undefined";
}

export const tokenStore = {
  getAccess(): string | null {
    if (!hasWindow()) return null;
    return window.localStorage.getItem(ACCESS_KEY);
  },

  getRefresh(): string | null {
    if (!hasWindow()) return null;
    return window.localStorage.getItem(REFRESH_KEY);
  },

  setTokens(access: string, refresh: string) {
    if (!hasWindow()) return;
    window.localStorage.setItem(ACCESS_KEY, access);
    window.localStorage.setItem(REFRESH_KEY, refresh);
  },

  clear() {
    if (!hasWindow()) return;
    window.localStorage.removeItem(ACCESS_KEY);
    window.localStorage.removeItem(REFRESH_KEY);
  },
};