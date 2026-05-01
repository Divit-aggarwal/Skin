import { useState, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  Alert,
  Linking,
} from 'react-native';
import { router } from 'expo-router';
import { useQueryClient } from '@tanstack/react-query';
import { CameraView, useCameraPermissions } from 'expo-camera';
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

function parseUploadError(err: unknown): { isQualityFail: boolean; message: string } {
  const res = (err as { response?: { data?: { error?: { code?: string; message?: string } } } })
    .response?.data?.error;
  if (res?.code === 'IMAGE_QUALITY_FAILED') {
    return { isQualityFail: true, message: res.message ?? 'Image quality check failed.' };
  }
  return { isQualityFail: false, message: 'Connection failed. Check your WiFi and try again.' };
}

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

  const [permission, requestPermission] = useCameraPermissions();
  const cameraRef = useRef<CameraView>(null);

  const { pickFromGallery } = useImagePicker();
  const queryClient = useQueryClient();
  const setCurrentSession = useSessionStore((s) => s.setCurrentSession);
  const setCapturedImageUri = useSessionStore((s) => s.setCapturedImageUri);

  function handlePickResult(picked: PickedImage | null) {
    if (!picked) return;
    if (!checkSize(picked.fileSize)) {
      Alert.alert('Image Too Large', 'Please choose a photo under 3 MB.');
      return;
    }
    setCapturedImageUri(picked.uri);
    setImage(picked);
    setState('preview');
  }

  async function onCapture() {
    if (!cameraRef.current) return;
    const photo = await cameraRef.current.takePictureAsync({ quality: 0.85, base64: true });
    if (!photo) return;
    handlePickResult({
      uri: photo.uri,
      base64: photo.base64 ?? '',
      mimeType: 'image/jpeg',
      fileSize: undefined,
    });
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
      queryClient.invalidateQueries({ queryKey: ['analysis', 'history'] });
      router.replace(`/(app)/report/${session.id}`);
    } catch (err) {
      const { isQualityFail, message } = parseUploadError(err);
      if (isQualityFail) {
        setQualityReason(message);
        setState('quality_failed');
      } else {
        setErrorMessage(message);
        setState('error');
      }
    }
  }

  async function onRetryAnalysis() {
    if (!image || !imageId) { onRetake(); return; }
    setState('analysing');
    try {
      const { data: session } = await analysisApi.createSession(imageId, image.base64);
      setCurrentSession(session.id);
      queryClient.invalidateQueries({ queryKey: ['analysis', 'history'] });
      router.replace(`/(app)/report/${session.id}`);
    } catch {
      setErrorMessage('Analysis failed. Please try again.');
      setState('error');
    }
  }

  async function onRetryUpload() {
    if (!image) { onRetake(); return; }
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
      queryClient.invalidateQueries({ queryKey: ['analysis', 'history'] });
      router.replace(`/(app)/report/${session.id}`);
    } catch (err) {
      const { isQualityFail, message } = parseUploadError(err);
      if (isQualityFail) {
        setQualityReason(message);
        setState('quality_failed');
      } else {
        setErrorMessage(message);
        setState('error');
      }
    }
  }

  if (!permission) {
    return <View style={styles.root} />;
  }

  if (!permission.granted) {
    return (
      <View style={[styles.root, styles.permissionRoot]}>
        <Text style={styles.permissionText}>Camera access required</Text>
        <TouchableOpacity
          style={styles.settingsBtn}
          onPress={permission.canAskAgain ? requestPermission : () => Linking.openSettings()}
          activeOpacity={0.85}
        >
          <Text style={styles.settingsBtnText}>Open Settings</Text>
        </TouchableOpacity>
      </View>
    );
  }

  if (state === 'idle') {
    return (
      <View style={styles.root}>
        <CameraView ref={cameraRef} style={StyleSheet.absoluteFill} facing="front" />
        <View style={styles.ovalOverlay}>
          <View style={styles.cameraOval}>
            <Corner position="topLeft" />
            <Corner position="topRight" />
            <Corner position="bottomLeft" />
            <Corner position="bottomRight" />
          </View>
          <Text style={styles.hint}>Position your face within the oval</Text>
        </View>
        <View style={styles.captureBar}>
          <TouchableOpacity style={styles.captureBtn} onPress={onCapture} activeOpacity={0.85}>
            <View style={styles.captureInner} />
          </TouchableOpacity>
          <TouchableOpacity onPress={onGallery} activeOpacity={0.7} style={styles.galleryTouchable}>
            <Text style={styles.galleryText}>Choose from gallery</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.root}>
      <View style={styles.ovalContainer}>
        <View style={styles.oval}>
          {image && <Image source={{ uri: image.uri }} style={styles.preview} />}
          <Corner position="topLeft" />
          <Corner position="topRight" />
          <Corner position="bottomLeft" />
          <Corner position="bottomRight" />
        </View>
      </View>

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

const OVAL_W = 300;
const OVAL_H = 380;

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: '#0a0a0a',
    alignItems: 'center',
  },
  // Permission denied
  permissionRoot: {
    justifyContent: 'center',
    gap: 20,
  },
  permissionText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  settingsBtn: {
    paddingHorizontal: 32,
    height: 48,
    backgroundColor: '#ffffff',
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  settingsBtnText: {
    color: '#0a0a0a',
    fontSize: 15,
    fontWeight: '600',
  },
  // Camera idle overlay
  ovalOverlay: {
    ...StyleSheet.absoluteFillObject,
    alignItems: 'center',
    justifyContent: 'center',
  },
  cameraOval: {
    width: OVAL_W,
    height: OVAL_H,
    borderRadius: 120,
    borderWidth: 2,
    borderStyle: 'dashed',
    borderColor: 'rgba(255,255,255,0.5)',
    marginBottom: 12,
  },
  captureBar: {
    position: 'absolute',
    bottom: 60,
    left: 0,
    right: 0,
    alignItems: 'center',
  },
  captureBtn: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: '#ffffff',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  captureInner: {
    width: 52,
    height: 52,
    borderRadius: 26,
    backgroundColor: '#0a0a0a',
  },
  galleryTouchable: {
    padding: 8,
  },
  galleryText: {
    color: 'rgba(255,255,255,0.6)',
    fontSize: 13,
  },
  // Preview / non-idle states
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
    fontSize: 13,
    textAlign: 'center',
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
