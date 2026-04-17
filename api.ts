"use client";

import { tokenStore } from "./auth";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";


async function refreshAccessToken(): Promise<string | null> {
  const refresh = tokenStore.getRefresh();
  if (!refresh) return null;

  const res = await fetch(`${API_BASE}/api/auth/refresh/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ refresh }),
  });

  if (!res.ok) return null;

  const data = await res.json();
  const newAccess = data?.access as string | undefined;

  if (!newAccess) return null;

  tokenStore.setTokens(newAccess, refresh);
  return newAccess;
}



export async function apiFetch(path: string, init: RequestInit = {}) {
  const headers = new Headers(init.headers || {});
  headers.set("Content-Type", "application/json");

  const setAuthHeader = () => {
    const access = tokenStore.getAccess();
    if (access) {
      headers.set("Authorization", `Bearer ${access}`);
    } else {
      headers.delete("Authorization");
    }
  };

  setAuthHeader();

  const doReq = () =>
    fetch(`${API_BASE}${path}`, {
      ...init,
      headers,
    });

  let res = await doReq();

  // access token expired болса refresh жасаймыз
  if (res.status === 401) {
    const newAccess = await refreshAccessToken();

    if (newAccess) {
      headers.set("Authorization", `Bearer ${newAccess}`);
      res = await doReq();
    }
  }

  if (!res.ok) {
    try {
      const j = await res.json();
      throw new Error(j?.detail || JSON.stringify(j));
    } catch {
      const t = await res.text().catch(() => "");
      throw new Error(t || `HTTP ${res.status}`);
    }
  }

  if (res.status === 204) return null;

  return res.json();
}



//
// JOBS
//

export function fetchJobs() {
  return apiFetch("/api/jobs/");
}

export function fetchJob(id: number) {
  return apiFetch(`/api/jobs/${id}/`);
}

export function createJob(data: any) {
  return apiFetch("/api/jobs/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function assignPerformer(jobId: number, performerId: number) {
  return apiFetch(`/api/jobs/${jobId}/assign/`, {
    method: "POST",
    body: JSON.stringify({
      performer_id: performerId,
    }),
  });
}

export function markDone(jobId: number) {
  return apiFetch(`/api/jobs/${jobId}/mark-done/`, {
    method: "POST",
  });
}



//
// BIDS
//

export function createBid(jobId: number, data: any) {
  return apiFetch(`/api/jobs/${jobId}/bids/`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function fetchJobBids(jobId: number) {
  return apiFetch(`/api/jobs/${jobId}/bids/`);
}

export function fetchMyBids() {
  return apiFetch(`/api/jobs/my-bids/`);
}



//
// MESSAGES / CHAT
//

export function fetchMessages(jobId: number) {
  return apiFetch(`/api/jobs/${jobId}/messages/`);
}

export function sendMessage(jobId: number, text: string) {
  return apiFetch(`/api/jobs/${jobId}/messages/`, {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}



//
// MY JOBS
//

export function fetchMyJobs() {
  return apiFetch(`/api/jobs/my-jobs/`);
}

export function fetchMyAssignedJobs() {
  return apiFetch(`/api/jobs/my-assigned-jobs/`);
}



//
// PROFILE
//

export function fetchMyProfile() {
  return apiFetch("/api/me/");
}

export function updateMyRole(role: string) {
  return apiFetch("/api/me/", {
    method: "POST",
    body: JSON.stringify({ role }),
  });
}



//
// NOTIFICATIONS
//

export function fetchNotifications(isRead?: boolean) {
  const q = typeof isRead === "boolean" ? `?is_read=${isRead}` : "";
  return apiFetch(`/api/notifications/${q}`);
}

export function unreadCount() {
  return apiFetch(`/api/notifications/unread-count/`);
}

export function markNotificationRead(id: number) {
  return apiFetch(`/api/notifications/${id}/read/`, {
    method: "POST",
  });
}

export function readAllNotifications() {
  return apiFetch(`/api/notifications/read-all/`, {
    method: "POST",
  }); 
}