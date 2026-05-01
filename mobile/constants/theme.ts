export const colors = {
  background: '#f8f7f4',
  surface: '#ffffff',
  primary: '#0a0a0a',
  textPrimary: '#0a0a0a',
  textSecondary: '#888888',
  textTertiary: '#aaaaaa',
  border: 'rgba(0,0,0,0.08)',
  success: '#1D9E75',
  warning: '#EF9F27',
  danger: '#E24B4A',
} as const;

export const typography = {
  fontSize: {
    xs: 10,
    sm: 12,
    md: 14,
    lg: 16,
    xl: 20,
    xxl: 26,
    xxxl: 32,
  },
  fontWeight: {
    regular: '400' as const,
    medium: '500' as const,
  },
} as const;

export const spacing = {
  1: 4,
  2: 8,
  3: 12,
  4: 16,
  5: 20,
  6: 24,
  8: 32,
  12: 48,
  16: 64,
} as const;

export const radius = {
  sm: 8,
  md: 12,
  lg: 16,
  xl: 20,
  full: 9999,
} as const;
