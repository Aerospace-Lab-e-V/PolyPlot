import { useMemo, useSyncExternalStore } from 'react'
import { readAttributionKey } from './attributionKey'

/**
 * The logo an attribution key holder uploads instead of the standard watermark logo. Like the key it
 * stays in this browser (never in the config) and is sent with every render request; the server uses
 * it only for a valid key (see check_logo_bytes and watermark in the backend).
 */
export type CustomLogo = { id: number; name: string; dataUrl: string }

/** The server refuses larger files (MAX_LOGO_BYTES in backend/security.py). */
export const MAX_LOGO_BYTES = 1_000_000
export const LOGO_FILE_ACCEPT = '.png,.jpg,.jpeg,.svg'
const STORAGE_KEY = 'ashby-custom-logo'
const MIME_BY_EXTENSION: Record<string, string> = { png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', svg: 'image/svg+xml' }

export type LogoFileProblem = 'type' | 'size' | 'storage'

const listeners = new Set<() => void>()
const notify = () => listeners.forEach((listener) => listener())

const readRaw = (): string | null => {
  try {
    return window.localStorage.getItem(STORAGE_KEY)
  } catch {
    return null
  }
}

function parseLogo(raw: string | null): CustomLogo | null {
  if (!raw) return null
  try {
    const value: unknown = JSON.parse(raw)
    const logo = value as Partial<CustomLogo> | null
    return logo && typeof logo.id === 'number' && typeof logo.name === 'string' && typeof logo.dataUrl === 'string' ? logo as CustomLogo : null
  } catch {
    return null
  }
}

export const readCustomLogo = (): CustomLogo | null => parseLogo(readRaw())

/** Stores the chosen file, or forgets the logo (null). Rejects with the problem as the message. */
export async function setCustomLogo(file: File | null): Promise<void> {
  if (!file) {
    try {
      window.localStorage.removeItem(STORAGE_KEY)
    } catch {
      // Storage blocked: nothing was kept.
    }
    notify()
    return
  }
  const mime = MIME_BY_EXTENSION[file.name.split('.').pop()?.toLowerCase() ?? '']
  if (!mime) throw new Error('type' satisfies LogoFileProblem)
  if (file.size > MAX_LOGO_BYTES) throw new Error('size' satisfies LogoFileProblem)
  const bytes = new Uint8Array(await file.arrayBuffer())
  let binary = ''
  for (let offset = 0; offset < bytes.length; offset += 0x8000) binary += String.fromCharCode(...bytes.subarray(offset, offset + 0x8000))
  const logo: CustomLogo = { id: Date.now(), name: file.name, dataUrl: `data:${mime};base64,${btoa(binary)}` }
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(logo))
  } catch {
    throw new Error('storage' satisfies LogoFileProblem)
  }
  notify()
}

/** The logo as a file for a multipart request. */
export function customLogoFile(logo: CustomLogo): File {
  const [header, data] = logo.dataUrl.split(',')
  const binary = atob(data ?? '')
  const bytes = Uint8Array.from(binary, (character) => character.charCodeAt(0))
  return new File([bytes], logo.name, { type: header?.slice(5, header.indexOf(';')) })
}

/** The logo to send with render requests: only while the attribution key is held. */
export const customLogoForRequest = (): CustomLogo | null => (readAttributionKey() ? readCustomLogo() : null)

const subscribe = (listener: () => void) => {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

if (typeof window !== 'undefined') {
  window.addEventListener('storage', (event) => {
    if (event.key === STORAGE_KEY || event.key === null) notify()
  })
}

export function useCustomLogo(): CustomLogo | null {
  const raw = useSyncExternalStore(subscribe, readRaw, () => null)
  return useMemo(() => parseLogo(raw), [raw])
}
