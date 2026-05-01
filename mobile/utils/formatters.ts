import type { SeverityLevel } from '../api/types';

export function getScoreColor(score: number): string {
  if (score < 33) return '#1D9E75';
  if (score <= 66) return '#EF9F27';
  return '#E24B4A';
}

export function getScoreLabel(score: number): string {
  if (score < 33) return 'Low';
  if (score <= 66) return 'Moderate';
  return 'High';
}

export function getSeverityColor(severity: SeverityLevel): string {
  if (severity === 'mild') return '#1D9E75';
  if (severity === 'moderate') return '#EF9F27';
  return '#E24B4A';
}

export function formatScanDate(isoString: string): string {
  const d = new Date(isoString);
  return d.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
    + ' at '
    + d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
}
