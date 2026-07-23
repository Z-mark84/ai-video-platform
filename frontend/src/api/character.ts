/** M7 角色一致性 - API服务层 */

import type { CharacterInfo, CharacterCreateRequest, ConsistencyScore } from './characterTypes'

const BASE = 'http://localhost:8000/api/v1/character'

async function req<T>(url: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...opts })
  if (!res.ok) throw new Error(((await res.json().catch(() => ({}))).detail) || res.statusText)
  return res.json()
}

export async function createCharacter(data: CharacterCreateRequest): Promise<CharacterInfo> {
  return req(`${BASE}/characters`, { method: 'POST', body: JSON.stringify(data) })
}

export async function getCharacters(): Promise<CharacterInfo[]> {
  return req(`${BASE}/characters`)
}

export async function getCharacter(id: string): Promise<CharacterInfo> {
  return req(`${BASE}/characters/${id}`)
}

export async function checkConsistency(id: string): Promise<ConsistencyScore> {
  return req(`${BASE}/characters/${id}/consistency`)
}
