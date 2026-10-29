import { getAccessToken } from "./auth"
import { errMsg, readJsonError } from "./error"

const base = import.meta.env.VITE_API_BASE_URL ?? ""

export type MeResponse = { id: string; email: string; is_admin: boolean }

export async function fetchMe(): Promise<MeResponse> {
  const token = getAccessToken()
  if (!token) throw new Error("Not signed in")
  const res = await fetch(`${base}/api/v1/me`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  const data = await readJsonError(res)
  if (!res.ok) throw new Error(errMsg(data, `${res.status}`))
  return data as MeResponse
}
