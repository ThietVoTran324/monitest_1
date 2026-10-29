import { getAccessToken } from "./auth"
import { errMsg, readJsonError } from "./error"

const base = import.meta.env.VITE_API_BASE_URL ?? ""

function authHeaders(): HeadersInit {
  const token = getAccessToken()
  if (!token) throw new Error("Not signed in")
  return { Authorization: `Bearer ${token}`, "Content-Type": "application/json" }
}

export type OutboxRow = {
  id: string
  monitor_id: string
  event_type: string
  to_email: string
  status: string
  attempts: number
  next_attempt_at: string | null
  last_error: string | null
  created_at: string | null
}

export async function listEmailOutbox(status?: string): Promise<OutboxRow[]> {
  const q = status ? `?status=${encodeURIComponent(status)}` : ""
  const res = await fetch(`${base}/api/v1/admin/email-outbox${q}`, { headers: authHeaders() })
  const data = await readJsonError(res)
  if (!res.ok) throw new Error(errMsg(data, `${res.status}`))
  return data as OutboxRow[]
}

export async function retryEmailOutbox(id: string): Promise<void> {
  const res = await fetch(`${base}/api/v1/admin/email-outbox/${id}/retry`, {
    method: "POST",
    headers: authHeaders(),
  })
  const data = await readJsonError(res)
  if (!res.ok) throw new Error(errMsg(data, `${res.status}`))
}

export async function grantAdmin(email: string): Promise<void> {
  const res = await fetch(`${base}/api/v1/admin/users/grant-admin`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ email }),
  })
  const data = await readJsonError(res)
  if (!res.ok) throw new Error(errMsg(data, `${res.status}`))
}

export async function patchMonitorOutboxSettings(
  monitorId: string,
  body: { alert_outbox_max_attempts?: number | null; alert_outbox_backoff_seconds?: string | null },
): Promise<void> {
  const res = await fetch(`${base}/api/v1/admin/monitors/${monitorId}/outbox-settings`, {
    method: "PATCH",
    headers: authHeaders(),
    body: JSON.stringify(body),
  })
  const data = await readJsonError(res)
  if (!res.ok) throw new Error(errMsg(data, `${res.status}`))
}
