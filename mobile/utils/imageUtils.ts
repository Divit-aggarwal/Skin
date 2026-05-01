const MAX_SIZE_BYTES = 3 * 1024 * 1024;

export function checkSize(fileSizeBytes: number | undefined): boolean {
  if (fileSizeBytes === undefined) return true;
  return fileSizeBytes <= MAX_SIZE_BYTES;
}

export function getMimeType(uri: string): 'image/jpeg' | 'image/png' | 'image/webp' {
  const lower = uri.toLowerCase();
  if (lower.endsWith('.png')) return 'image/png';
  if (lower.endsWith('.webp')) return 'image/webp';
  return 'image/jpeg';
}
