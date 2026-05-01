import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { useReport } from '../../../hooks/useReport';
import { useSessionStore } from '../../../store/sessionStore';
import { getScoreColor, getScoreLabel, getSeverityColor, formatScanDate } from '../../../utils/formatters';
import type { Detection, RecommendationOut, ZoneScore } from '../../../api/types';

const SCREEN_W = Dimensions.get('window').width;
const IMAGE_W = SCREEN_W - 32;
const IMAGE_H = IMAGE_W * (4 / 3);

// Phase 1: assume standard phone capture resolution.
// Phase 2: use actual image dimensions returned by the API.
const ORIG_W = 3024;
const ORIG_H = 4032;
const SCALE_X = IMAGE_W / ORIG_W;
const SCALE_Y = IMAGE_H / ORIG_H;

const ZONE_LABELS: Record<string, string> = {
  forehead: 'Forehead',
  nose: 'Nose',
  left_cheek: 'Left cheek',
  right_cheek: 'Right cheek',
  chin: 'Chin',
};

const REC_BG: Record<string, string> = {
  general:  '#EAF3DE',
  acne:     '#FCEBEB',
  oiliness: '#E6F1FB',
  wrinkle:  '#EEEDFE',
};

const REC_TEXT_COLOR: Record<string, string> = {
  general:  '#3A6B1F',
  acne:     '#8B2020',
  oiliness: '#1A4F7A',
  wrinkle:  '#4A3A8B',
};

function BackChevron() {
  return (
    <View style={chevron.wrap}>
      <View style={[chevron.arm, { transform: [{ rotate: '-45deg' }, { translateY: 2 }] }]} />
      <View style={[chevron.arm, { transform: [{ rotate: '45deg' }, { translateY: -2 }] }]} />
    </View>
  );
}

const chevron = StyleSheet.create({
  wrap: { width: 20, height: 20, justifyContent: 'center' },
  arm: { width: 10, height: 2, backgroundColor: '#ffffff', borderRadius: 1, marginLeft: 4 },
});

function MiniScoreCard({ label, score }: { label: string; score: number }) {
  const color = getScoreColor(score);
  const scoreLabel = getScoreLabel(score);
  return (
    <View style={styles.miniCard}>
      <Text style={styles.miniCardLabel}>{label}</Text>
      <Text style={[styles.miniCardScore, { color }]}>{Math.round(score)}</Text>
      <Text style={[styles.miniCardLevel, { color }]}>{scoreLabel}</Text>
    </View>
  );
}

function ZoneBar({ zone, score }: ZoneScore) {
  const barColor = getScoreColor(score);
  const label = ZONE_LABELS[zone] ?? zone;
  return (
    <View style={styles.zoneRow}>
      <Text style={styles.zoneLabel}>{label}</Text>
      <View style={styles.zoneBarTrack}>
        <View style={[styles.zoneBarFill, { width: `${score}%`, backgroundColor: barColor }]} />
      </View>
      <Text style={[styles.zoneScore, { color: barColor }]}>{Math.round(score)}</Text>
    </View>
  );
}

function DetectionDot({
  detection,
  zoneScore,
}: {
  detection: Detection;
  zoneScore: number;
}) {
  const [cx, cy] = detection.bbox;
  const dotColor = getScoreColor(zoneScore);
  const dotLeft = Math.round(cx * SCALE_X) - 8;
  const dotTop = Math.round(cy * SCALE_Y) - 8;
  return (
    <View style={[styles.detContainer, { top: dotTop, left: dotLeft }]}>
      <View style={[styles.detDot, { backgroundColor: dotColor }]} />
      <Text style={styles.detConf}>{Math.round(detection.confidence * 100)}%</Text>
    </View>
  );
}

function RecommendationCard({ rec }: { rec: RecommendationOut }) {
  const bg = REC_BG[rec.category] ?? '#F0F0F0';
  const textColor = REC_TEXT_COLOR[rec.category] ?? '#333333';
  return (
    <View style={[styles.recCard, { backgroundColor: bg }]}>
      <Text style={[styles.recCategory, { color: textColor }]}>
        {rec.category.toUpperCase()}
      </Text>
      <Text style={[styles.recText, { color: textColor }]}>{rec.text}</Text>
    </View>
  );
}

export default function ReportScreen() {
  const { sessionId } = useLocalSearchParams<{ sessionId: string }>();
  const capturedImageUri = useSessionStore((s) => s.capturedImageUri);
  const { data, isLoading, isError } = useReport(sessionId ?? '');

  if (isLoading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#888888" />
      </View>
    );
  }

  if (isError || !data?.data?.report) {
    return (
      <View style={styles.centered}>
        <Text style={styles.errorText}>Failed to load report.</Text>
        <TouchableOpacity style={styles.backBtn} onPress={() => router.back()}>
          <Text style={styles.backBtnText}>Go back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const session = data.data;
  const report = session.report!;
  const recs = [...session.recommendations].sort((a, b) => a.priority - b.priority);
  const severityColor = getSeverityColor(report.severity_level);
  const severityLabel = report.severity_level.charAt(0).toUpperCase() + report.severity_level.slice(1);
  const zones = report.zone_breakdown ?? [];
  const detections = report.detections ?? [];
  const hasImage = !!capturedImageUri;

  // Build zone → score lookup for dot coloring
  const zoneScoreMap = new Map(zones.map((z) => [z.zone, z.score]));

  // Only render dots for detections whose zone score > 5
  const visibleDetections = detections.filter((d) => (zoneScoreMap.get(d.zone) ?? 0) > 5);
  const showNoAcne = visibleDetections.length === 0;

  return (
    <ScrollView style={styles.root} showsVerticalScrollIndicator={false}>
      {/* ── Hero ── */}
      <View style={styles.hero}>
        <TouchableOpacity style={styles.heroBack} onPress={() => router.back()} activeOpacity={0.7}>
          <BackChevron />
        </TouchableOpacity>

        <Text style={styles.heroDate}>{formatScanDate(report.created_at)}</Text>

        <View style={[styles.severityPill, { backgroundColor: severityColor }]}>
          <Text style={styles.severityPillText}>{severityLabel}</Text>
        </View>

        <Text style={styles.overallScore}>{Math.round(report.overall_score)}</Text>
        <Text style={styles.overallScoreLabel}>Overall skin score</Text>

        <View style={styles.miniCards}>
          <MiniScoreCard label="ACNE" score={report.acne_score} />
          <MiniScoreCard label="WRINKLE" score={report.wrinkle_score} />
          <MiniScoreCard label="OILINESS" score={report.oiliness_score} />
        </View>
      </View>

      {/* ── Detail ── */}
      <View style={styles.detail}>

        {/* Zone breakdown */}
        <Text style={styles.sectionTitle}>Zone breakdown</Text>
        <View style={styles.card}>
          {zones.length > 0
            ? zones.map((z) => <ZoneBar key={z.zone} zone={z.zone} score={z.score} />)
            : <Text style={styles.emptyText}>No zone data available.</Text>
          }
        </View>

        {/* Annotated image */}
        <Text style={styles.sectionTitle}>Detected zones</Text>
        {hasImage ? (
          <View style={styles.imageWrapper}>
            <Image source={{ uri: capturedImageUri! }} style={styles.faceImage} resizeMode="cover" />
            {visibleDetections.map((det, i) => (
              <DetectionDot
                key={i}
                detection={det}
                zoneScore={zoneScoreMap.get(det.zone) ?? 50}
              />
            ))}
            {showNoAcne && (
              <View style={styles.noDetectionOverlay}>
                <Text style={styles.noDetectionText}>No acne detected</Text>
              </View>
            )}
          </View>
        ) : (
          <View style={[styles.imageWrapper, styles.imagePlaceholder]}>
            <Text style={styles.noImageText}>Photo not available</Text>
          </View>
        )}
        <Text style={styles.imageCaption}>
          Front-facing photos give the most accurate zone detection
        </Text>

        {/* Recommendations */}
        {recs.length > 0 && (
          <>
            <Text style={styles.sectionTitle}>Recommendations</Text>
            {recs.map((rec) => (
              <RecommendationCard key={rec.id} rec={rec} />
            ))}
          </>
        )}

        {/* Model version footer */}
        <Text style={styles.modelVersion}>{report.model_version}</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: '#f8f7f4' },
  centered: {
    flex: 1, backgroundColor: '#f8f7f4',
    alignItems: 'center', justifyContent: 'center', padding: 24,
  },
  errorText: { fontSize: 15, color: '#0a0a0a', marginBottom: 20, textAlign: 'center' },
  backBtn: {
    paddingHorizontal: 24, paddingVertical: 12,
    backgroundColor: '#0a0a0a', borderRadius: 12,
  },
  backBtnText: { color: '#fff', fontSize: 14, fontWeight: '600' },

  // Hero
  hero: {
    backgroundColor: '#0a0a0a',
    paddingTop: 56,
    paddingBottom: 32,
    paddingHorizontal: 20,
  },
  heroBack: {
    position: 'absolute',
    top: 56,
    left: 16,
    padding: 8,
    zIndex: 10,
  },
  heroDate: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.4)',
    textAlign: 'center',
    marginBottom: 12,
  },
  severityPill: {
    alignSelf: 'center',
    paddingHorizontal: 14,
    paddingVertical: 5,
    borderRadius: 999,
    marginBottom: 16,
  },
  severityPillText: { color: '#fff', fontSize: 12, fontWeight: '600' },
  overallScore: {
    fontSize: 52,
    fontWeight: '700',
    color: '#ffffff',
    textAlign: 'center',
    lineHeight: 60,
  },
  overallScoreLabel: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.4)',
    textAlign: 'center',
    marginBottom: 24,
    marginTop: 4,
  },
  miniCards: { flexDirection: 'row', gap: 8 },
  miniCard: {
    flex: 1,
    backgroundColor: 'rgba(255,255,255,0.07)',
    borderRadius: 12,
    padding: 12,
    alignItems: 'center',
  },
  miniCardLabel: {
    fontSize: 10,
    color: 'rgba(255,255,255,0.4)',
    fontWeight: '600',
    letterSpacing: 0.5,
    marginBottom: 6,
  },
  miniCardScore: { fontSize: 22, fontWeight: '700', marginBottom: 2 },
  miniCardLevel: { fontSize: 11, fontWeight: '500' },

  // Detail
  detail: { padding: 16, paddingBottom: 48 },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#0a0a0a',
    marginTop: 20,
    marginBottom: 10,
  },
  card: { backgroundColor: '#ffffff', borderRadius: 16, padding: 16 },
  emptyText: { fontSize: 13, color: '#888888', textAlign: 'center', paddingVertical: 8 },

  // Zone bars
  zoneRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 10 },
  zoneLabel: { width: 90, fontSize: 13, color: '#0a0a0a' },
  zoneBarTrack: {
    flex: 1,
    height: 6,
    backgroundColor: 'rgba(0,0,0,0.07)',
    borderRadius: 3,
    overflow: 'hidden',
    marginRight: 10,
  },
  zoneBarFill: { height: 6, borderRadius: 3 },
  zoneScore: { width: 28, fontSize: 12, fontWeight: '600', textAlign: 'right' },

  // Annotated image
  imageWrapper: {
    width: IMAGE_W,
    height: IMAGE_H,
    borderRadius: 16,
    overflow: 'hidden',
    backgroundColor: '#e0e0e0',
  },
  faceImage: { width: IMAGE_W, height: IMAGE_H },
  detContainer: {
    position: 'absolute',
    alignItems: 'center',
  },
  detDot: {
    width: 16,
    height: 16,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#ffffff',
  },
  detConf: {
    color: '#ffffff',
    fontSize: 9,
    fontWeight: '600',
    marginTop: 2,
    textShadowColor: 'rgba(0,0,0,0.8)',
    textShadowOffset: { width: 0, height: 1 },
    textShadowRadius: 2,
  },
  noDetectionOverlay: {
    position: 'absolute',
    bottom: 16,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  noDetectionText: {
    color: '#ffffff',
    fontSize: 13,
    backgroundColor: 'rgba(0,0,0,0.5)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
  },
  imagePlaceholder: { alignItems: 'center', justifyContent: 'center' },
  noImageText: { fontSize: 13, color: '#888888' },
  imageCaption: { fontSize: 12, color: '#aaaaaa', textAlign: 'center', marginTop: 8 },

  // Recommendations
  recCard: { borderRadius: 12, padding: 14, marginBottom: 10 },
  recCategory: { fontSize: 10, fontWeight: '700', letterSpacing: 0.8, marginBottom: 6 },
  recText: { fontSize: 13, lineHeight: 19 },

  // Footer
  modelVersion: { textAlign: 'center', fontSize: 10, color: '#cccccc', marginTop: 32 },
});
