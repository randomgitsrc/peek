const MIME_MAP: Record<string, string> = {
  png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg',
  gif: 'image/gif', webp: 'image/webp', svg: 'image/svg+xml',
  ico: 'image/x-icon', bmp: 'image/bmp',
  woff: 'font/woff', woff2: 'font/woff2',
  ttf: 'font/ttf', otf: 'font/otf',
}

export function guessMimeType(filename: string): string | null {
  const ext = filename.split('.').pop()?.toLowerCase() ?? ''
  return MIME_MAP[ext] ?? null
}