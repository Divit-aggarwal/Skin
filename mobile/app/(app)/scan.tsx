import { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  Alert,
  ScrollView,
} from 'react-native';
import { router } from 'expo-router';
import { useImagePicker } from '../../hooks/useImagePicker';
import { checkSize } from '../../utils/imageUtils';
import { imagesApi } from '../../api/images';
import { analysisApi } from '../../api/analysis';
import { useSessionStore } from '../../store/sessionStore';

type ScanState =
  | 'idle'
  | 'preview'
  | 'uploading'
  | 'quality_failed'
  | 'analysing'
  | 'error';

interface PickedImage {
  uri: string;
  base64: string;
  mimeType: string;
  fileSize: number | undefined;
}

export default function ScanScreen() {
  const [state, setState] = useState<ScanState>('idle');
  const [image, setImage] = useState<PickedImage | null>(null);
  const [qualityReason, setQualityReason] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [imageId, setImageId] = useState<string | null>(null);

  const { pickFromCamera, pickFromGallery } = useImagePicker();
  const setCurrentSession = useSessionStore((s) => s.setCurrentSession);

  function handlePickResult(picked: PickedImage | null) {
    if (!picked) return;
    if (!checkSize(picked.fileSize)) {
      Alert.alert('Image Too Large', 'Please choose a photo under 3 MB.');
      return;
    }
    setImage(picked);
    setState('preview');
  }

  async function onCamera() {
    const picked = await pickFromCamera();
    handlePickResult(picked);
  }

  async function onGallery() {
    const picked = await pickFromGallery();
    handlePickResult(picked);
  }

  function onRetake() {
    setImage(null);
    setImageId(null);
    setState('idle');
  }

  async function onUsePhoto() {
    if (!image) return;
    setState('uploading');
    try {
      const { data: imageOut } = await imagesApi.upload(image.base64, image.mimeType);
      if (!imageOut.quality_passed) {
        setQualityReason(imageOut.quality_reason ?? 'Image quality check failed.');
        setState('quality_failed');
        return;
      }
      setImageId(imageOut.id);
      setState('analysing');
      const { data: session } = await analysisApi.createSession(imageOut.id, image.base64);
      setCurrentSession(session.id);
      router.replace(`/(app)/report/${session.id}`);
    } catch {
      setErrorMessage('Connection failed. Check your WiFi and try again.');
      setState('error');
    }
  }

  async function onRetryAnalysis() {
    if (!image || !imageId) {
      onRetake();
      return;
    }
    setState('analysing');
    try {
      const { data: session } = await analysisApi.createSession(imageId, image.base64);
      setCurrentSession(session.id);
      router.replace(`/(app)/report/${session.id}`);
    } catch {
      setErrorMessage('Analysis failed. Please try again.');
      setState('error');
    }
  }

  async function onRetryUpload() {
    if (!image) {
      onRetake();
      return;
    }
    setState('uploading');
    try {
      const { data: imageOut } = await imagesApi.upload(image.base64, image.mimeType);
      if (!imageOut.quality_passed) {
        setQualityReason(imageOut.quality_reason ?? 'Image quality check failed.');
        setState('quality_failed');
        return;
      }
      setImageId(imageOut.id);
      setState('analysing');
      const { data: session } = await analysisApi.createSession(imageOut.id, image.base64);
      setCurrentSession(session.id);
      router.replace(`/(app)/report/${session.id}`);
    } catch {
      setErrorMessage('Connection failed. Check your WiFi and try again.');
      setState('error');
    }
  }

  return (
    <View style={styles.root}>
      {/* Oval frame always visible */}
      <View style={styles.ovalContainer}>
        <View style={styles.oval}>
          {image ? (
            <Image source={{ uri: image.uri }} style={styles.preview} />
          ) : (
            <View style={styles.ovalInner} />
          )}
          <Corner position="topLeft" />
          <Corner position="topRight" />
          <Corner position="bottomLeft" />
          <Corner position="bottomRight" />
        </View>
      </View>

      {state === 'idle' && <IdleContent onCamera={onCamera} onGallery={onGallery} />}

      {state === 'preview' && (
        <PreviewContent onUse={onUsePhoto} onRetake={onRetake} />
      )}

      {state === 'uploading' && (
        <StatusContent label="Checking image quality..." onAbort={onRetake} />
      )}

      {state === 'analysing' && (
        <StatusContent label="Analysing your skin..." onAbort={onRetake} />
      )}

      {state === 'quality_failed' && (
        <QualityFailedContent reason={qualityReason} onRetry={onRetake} />
      )}

      {state === 'error' && (
        <ErrorContent
          message={errorMessage}
          onRetry={imageId ? onRetryAnalysis : onRetryUpload}
          onRetake={onRetake}
        />
      )}
    </View>
  );
}

// ── Corner brackets ──────────────────────────────────────────────────────────

type CornerPosition = 'topLeft' | 'topRight' | 'bottomLeft' | 'bottomRight';

function Corner({ position }: { position: CornerPosition }) {
  const isTop = position === 'topLeft' || position === 'topRight';
  const isLeft = position === 'topLeft' || position === 'bottomLeft';

  return (
    <View
      style={[
        styles.corner,
        isTop ? { top: -1 } : { bottom: -1 },
        isLeft ? { left: -1 } : { right: -1 },
        {
          borderTopWidth: isTop ? 2 : 0,
          borderBottomWidth: isTop ? 0 : 2,
          borderLeftWidth: isLeft ? 2 : 0,
          borderRightWidth: isLeft ? 0 : 2,
        },
      ]}
    />
  );
}

// ── Sub-components ───────────────────────────────────────────────────────────

function IdleContent({
  onCamera,
  onGallery,
}: {
  onCamera: () => void;
  onGallery: () => void;
}) {
  return (
    <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
      <Text style={styles.hint}>Position your face inside the frame</Text>
      <View style={styles.tips}>
        <TipRow text="Good lighting, face the source" />
        <TipRow text="Face fills most of the frame" />
        <TipRow text="Remove glasses for best results" />
      </View>
      <TouchableOpacity style={styles.primaryBtn} onPress={onCamera} activeOpacity={0.85}>
        <Text style={styles.primaryBtnText}>Take photo</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.ghostBtn} onPress={onGallery} activeOpacity={0.7}>
        <Text style={styles.ghostBtnText}>Choose from gallery</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

function TipRow({ text }: { text: string }) {
  return (
    <View style={styles.tipRow}>
      <View style={styles.tipDot} />
      <Text style={styles.tipText}>{text}</Text>
    </View>
  );
}

function PreviewContent({ onUse, onRetake }: { onUse: () => void; onRetake: () => void }) {
  return (
    <View style={styles.content}>
      <TouchableOpacity style={styles.primaryBtn} onPress={onUse} activeOpacity={0.85}>
        <Text style={styles.primaryBtnText}>Use this photo</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.ghostBtn} onPress={onRetake} activeOpacity={0.7}>
        <Text style={styles.ghostBtnText}>Retake</Text>
      </TouchableOpacity>
    </View>
  );
}

function StatusContent({ label, onAbort }: { label: string; onAbort: () => void }) {
  return (
    <View style={styles.content}>
      <ActivityIndicator color="#ffffff" size="large" style={{ marginBottom: 16 }} />
      <Text style={styles.statusLabel}>{label}</Text>
      <TouchableOpacity style={styles.ghostBtn} onPress={onAbort} activeOpacity={0.7}>
        <Text style={styles.ghostBtnText}>Cancel</Text>
      </TouchableOpacity>
    </View>
  );
}

function QualityFailedContent({ reason, onRetry }: { reason: string; onRetry: () => void }) {
  return (
    <View style={styles.content}>
      <Text style={styles.errorTitle}>Photo didn't pass quality check</Text>
      <Text style={styles.errorReason}>{reason}</Text>
      <TouchableOpacity style={styles.primaryBtn} onPress={onRetry} activeOpacity={0.85}>
        <Text style={styles.primaryBtnText}>Try again</Text>
      </TouchableOpacity>
    </View>
  );
}

function ErrorContent({
  message,
  onRetry,
  onRetake,
}: {
  message: string;
  onRetry: () => void;
  onRetake: () => void;
}) {
  return (
    <View style={styles.content}>
      <Text style={styles.errorTitle}>Something went wrong</Text>
      <Text style={styles.errorReason}>{message}</Text>
      <TouchableOpacity style={styles.primaryBtn} onPress={onRetry} activeOpacity={0.85}>
        <Text style={styles.primaryBtnText}>Retry</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.ghostBtn} onPress={onRetake} activeOpacity={0.7}>
        <Text style={styles.ghostBtnText}>Start over</Text>
      </TouchableOpacity>
    </View>
  );
}

// ── Styles ───────────────────────────────────────────────────────────────────

const OVAL_W = 240;
const OVAL_H = 300;

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#0a0a0a',
    alignItems: 'center',
  },
  ovalContainer: {
    marginTop: 72,
    marginBottom: 32,
  },
  oval: {
    width: OVAL_W,
    height: OVAL_H,
    borderRadius: 120,
    borderWidth: 2,
    borderStyle: 'dashed',
    borderColor: 'rgba(255,255,255,0.25)',
    overflow: 'hidden',
    alignItems: 'center',
    justifyContent: 'center',
  },
  ovalInner: {
    width: '100%',
    height: '100%',
  },
  preview: {
    width: OVAL_W,
    height: OVAL_H,
    borderRadius: 120,
  },
  corner: {
    position: 'absolute',
    width: 20,
    height: 20,
    borderColor: '#ffffff',
  },
  content: {
    width: '100%',
    paddingHorizontal: 32,
    alignItems: 'center',
  },
  hint: {
    color: 'rgba(255,255,255,0.6)',
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 16,
  },
  tips: {
    alignSelf: 'stretch',
    marginBottom: 32,
    gap: 8,
  },
  tipRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  tipDot: {
    width: 4,
    height: 4,
    borderRadius: 2,
    backgroundColor: 'rgba(255,255,255,0.4)',
  },
  tipText: {
    color: 'rgba(255,255,255,0.5)',
    fontSize: 13,
  },
  primaryBtn: {
    width: '100%',
    height: 52,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  primaryBtnText: {
    color: '#0a0a0a',
    fontSize: 15,
    fontWeight: '600',
  },
  ghostBtn: {
    width: '100%',
    height: 52,
    alignItems: 'center',
    justifyContent: 'center',
  },
  ghostBtnText: {
    color: 'rgba(255,255,255,0.5)',
    fontSize: 15,
  },
  statusLabel: {
    color: 'rgba(255,255,255,0.6)',
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 24,
  },
  errorTitle: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
    marginBottom: 10,
  },
  errorReason: {
    color: 'rgba(255,255,255,0.55)',
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 28,
    lineHeight: 20,
  },
});
