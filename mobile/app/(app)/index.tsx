import { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { router } from 'expo-router';
import { useQuery } from '@tanstack/react-query';
import { useProfile } from '../../hooks/useProfile';
import { useUserStore } from '../../store/userStore';
import { analysisApi } from '../../api/analysis';
import type { SeverityLevel } from '../../api/types';
import { colors, typography, spacing, radius } from '../../constants/theme';

function getGreeting() {
  const h = new Date().getHours();
  if (h < 12) return 'Good morning';
  if (h < 17) return 'Good afternoon';
  return 'Good evening';
}

function getInitials(displayName: string | null, email: string | null): string {
  if (displayName?.trim()) {
    const parts = displayName.trim().split(' ');
    return parts.length >= 2
      ? (parts[0][0] + parts[1][0]).toUpperCase()
      : parts[0][0].toUpperCase();
  }
  return email ? email[0].toUpperCase() : '?';
}

function severityColor(level: SeverityLevel): string {
  if (level === 'mild') return colors.success;
  if (level === 'moderate') return colors.warning;
  return colors.danger;
}

function scoreColor(score: number): string {
  if (score < 33) return colors.success;
  if (score <= 66) return colors.warning;
  return colors.danger;
}

export default function HomeScreen() {
  const { isLoading, isSuccess } = useProfile();
  const user = useUserStore((s) => s.user);
  const profile = useUserStore((s) => s.profile);
  const profileSetupSeen = useUserStore((s) => s.profileSetupSeen);

  useEffect(() => {
    if (isSuccess && !profile?.skin_type && !profileSetupSeen) {
      router.replace('/(app)/profile-setup');
    }
  }, [isSuccess, profile?.skin_type, profileSetupSeen]);

  const { data: historyData, isLoading: historyLoading } = useQuery({
    queryKey: ['analysis', 'history', 'last'],
    queryFn: () => analysisApi.getHistory(1, 1),
    enabled: isSuccess,
    staleTime: 2 * 60 * 1000,
  });

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator color={colors.textSecondary} />
      </View>
    );
  }

  const displayName = profile?.display_name ?? null;
  const initials = getInitials(displayName, user?.email ?? null);
  const lastItem = historyData?.data.items[0] ?? null;

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      showsVerticalScrollIndicator={false}
    >
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerText}>
          <Text style={styles.greeting}>{getGreeting()},</Text>
          <Text style={styles.name}>{displayName ?? user?.email?.split('@')[0] ?? 'there'}</Text>
        </View>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>{initials}</Text>
        </View>
      </View>

      {/* Last scan card */}
      <View style={styles.scanCard}>
        {historyLoading ? (
          <View style={styles.scanCardEmpty}>
            <ActivityIndicator color="rgba(255,255,255,0.4)" />
          </View>
        ) : lastItem?.overall_score != null && lastItem.severity_level ? (
          <>
            <Text style={styles.cardLabel}>LATEST SCAN</Text>
            <View style={styles.scoreRow}>
              <Text style={[styles.scoreNumber, { color: scoreColor(lastItem.overall_score) }]}>
                {Math.round(lastItem.overall_score)}
              </Text>
              <View style={[styles.severityBadge, { backgroundColor: severityColor(lastItem.severity_level) }]}>
                <Text style={styles.severityText}>
                  {lastItem.severity_level.charAt(0).toUpperCase() + lastItem.severity_level.slice(1)}
                </Text>
              </View>
            </View>
          </>
        ) : (
          <View style={styles.scanCardEmpty}>
            <Text style={styles.emptyTitle}>No scans yet</Text>
            <Text style={styles.emptySubtitle}>Take your first skin scan to get started</Text>
            <TouchableOpacity
              style={styles.emptyButton}
              onPress={() => router.push('/(app)/scan')}
            >
              <Text style={styles.emptyButtonText}>Scan your skin</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>

      {/* CTA button */}
      <TouchableOpacity
        style={styles.ctaButton}
        onPress={() => router.push('/(app)/scan')}
      >
        <Text style={styles.ctaText}>Scan your skin now</Text>
      </TouchableOpacity>

      {/* Tips section */}
      <Text style={styles.sectionTitle}>Daily tips</Text>
      <View style={styles.tipCard}>
        <Text style={styles.tipEmoji}>☀️</Text>
        <View style={styles.tipBody}>
          <Text style={styles.tipTitle}>Apply SPF every morning</Text>
          <Text style={styles.tipDesc}>UV damage is the leading cause of premature ageing. SPF 30+ daily is non-negotiable.</Text>
        </View>
      </View>
      <View style={styles.tipCard}>
        <Text style={styles.tipEmoji}>💧</Text>
        <View style={styles.tipBody}>
          <Text style={styles.tipTitle}>
            {lastItem?.severity_level === 'severe'
              ? 'Stick to a gentle cleanser'
              : lastItem?.severity_level === 'moderate'
              ? 'Add a niacinamide serum'
              : 'Stay consistent with your routine'}
          </Text>
          <Text style={styles.tipDesc}>
            {lastItem
              ? 'Based on your latest scan results.'
              : 'Scan your skin to get personalised recommendations.'}
          </Text>
        </View>
      </View>
    </ScrollView>
  );
}

function MiniCard({ label, score }: { label: string; score: number }) {
  return (
    <View style={styles.miniCard}>
      <Text style={styles.miniLabel}>{label}</Text>
      <Text style={styles.miniScore}>{Math.round(score)}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1, justifyContent: 'center', alignItems: 'center',
    backgroundColor: colors.background,
  },
  container: { flex: 1, backgroundColor: colors.background },
  content: { paddingHorizontal: spacing[5], paddingTop: spacing[16], paddingBottom: spacing[8] },

  // Header
  header: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: spacing[6] },
  headerText: { flex: 1 },
  greeting: { fontSize: typography.fontSize.md, color: colors.textSecondary },
  name: { fontSize: typography.fontSize.xxl, fontWeight: '600', color: colors.textPrimary },
  avatar: {
    width: 44, height: 44, borderRadius: 22,
    backgroundColor: colors.primary,
    alignItems: 'center', justifyContent: 'center',
  },
  avatarText: { color: '#fff', fontSize: typography.fontSize.md, fontWeight: '600' },

  // Scan card
  scanCard: {
    backgroundColor: '#0a0a0a',
    borderRadius: radius.xl,
    padding: spacing[5],
    marginBottom: spacing[4],
    minHeight: 160,
  },
  cardLabel: {
    fontSize: typography.fontSize.xs,
    fontWeight: '500',
    color: 'rgba(255,255,255,0.4)',
    letterSpacing: 1,
    marginBottom: spacing[2],
  },
  scoreRow: { flexDirection: 'row', alignItems: 'center', gap: spacing[3], marginBottom: spacing[4] },
  scoreNumber: { fontSize: 52, fontWeight: '500', lineHeight: 60 },
  severityBadge: {
    paddingHorizontal: 10, paddingVertical: 4,
    borderRadius: radius.full,
  },
  severityText: { color: '#fff', fontSize: typography.fontSize.xs, fontWeight: '600' },
  miniCards: { flexDirection: 'row', gap: spacing[2] },
  miniCard: {
    flex: 1,
    backgroundColor: 'rgba(255,255,255,0.07)',
    borderRadius: radius.md,
    padding: spacing[3],
  },
  miniLabel: { fontSize: typography.fontSize.xs, color: 'rgba(255,255,255,0.5)', marginBottom: 4 },
  miniScore: { fontSize: typography.fontSize.xl, fontWeight: '500', color: '#fff' },

  // Empty state
  scanCardEmpty: { flex: 1, alignItems: 'center', justifyContent: 'center', paddingVertical: spacing[4] },
  emptyTitle: { fontSize: typography.fontSize.lg, fontWeight: '500', color: '#fff', marginBottom: spacing[1] },
  emptySubtitle: { fontSize: typography.fontSize.sm, color: 'rgba(255,255,255,0.5)', marginBottom: spacing[4], textAlign: 'center' },
  emptyButton: {
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.3)',
    borderRadius: radius.full, paddingHorizontal: 20, paddingVertical: 10,
  },
  emptyButtonText: { color: '#fff', fontSize: typography.fontSize.sm, fontWeight: '500' },

  // CTA
  ctaButton: {
    backgroundColor: colors.primary,
    borderRadius: radius.lg,
    paddingVertical: 16,
    alignItems: 'center',
    marginBottom: spacing[8],
  },
  ctaText: { color: '#fff', fontSize: 15, fontWeight: '500' },

  // Tips
  sectionTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing[3],
  },
  tipCard: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    borderWidth: 0.5,
    borderColor: 'rgba(0,0,0,0.06)',
    borderRadius: radius.lg,
    padding: spacing[4] - 2,
    marginBottom: spacing[3],
    gap: spacing[3],
    alignItems: 'flex-start',
  },
  tipEmoji: { fontSize: 20, marginTop: 2 },
  tipBody: { flex: 1 },
  tipTitle: { fontSize: typography.fontSize.md, fontWeight: '500', color: colors.textPrimary, marginBottom: 4 },
  tipDesc: { fontSize: typography.fontSize.sm, color: colors.textSecondary, lineHeight: 18 },
});
