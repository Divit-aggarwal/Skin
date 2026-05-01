import { Alert, Linking } from 'react-native';
import * as ImagePicker from 'expo-image-picker';

interface PickResult {
  uri: string;
  base64: string;
  mimeType: string;
  fileSize: number | undefined;
}

const PICKER_OPTIONS: ImagePicker.ImagePickerOptions = {
  mediaTypes: ImagePicker.MediaTypeOptions.Images,
  quality: 0.85,
  allowsEditing: true,
  aspect: [1, 1],
  base64: true,
};

function showSettingsAlert(permissionType: string) {
  Alert.alert(
    `${permissionType} Access Required`,
    `Please allow ${permissionType.toLowerCase()} access in Settings to scan your skin.`,
    [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Open Settings', onPress: () => Linking.openSettings() },
    ],
  );
}

function buildResult(asset: ImagePicker.ImagePickerAsset): PickResult | null {
  if (!asset.base64) return null;
  const lower = asset.uri.toLowerCase();
  const mimeType = lower.endsWith('.png')
    ? 'image/png'
    : lower.endsWith('.webp')
    ? 'image/webp'
    : 'image/jpeg';
  return { uri: asset.uri, base64: asset.base64, mimeType, fileSize: asset.fileSize };
}

export function useImagePicker() {
  async function pickFromCamera(): Promise<PickResult | null> {
    const { status } = await ImagePicker.requestCameraPermissionsAsync();
    if (status !== 'granted') {
      showSettingsAlert('Camera');
      return null;
    }
    const result = await ImagePicker.launchCameraAsync(PICKER_OPTIONS);
    if (result.canceled || !result.assets[0]) return null;
    return buildResult(result.assets[0]);
  }

  async function pickFromGallery(): Promise<PickResult | null> {
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      showSettingsAlert('Photo Library');
      return null;
    }
    const result = await ImagePicker.launchImageLibraryAsync(PICKER_OPTIONS);
    if (result.canceled || !result.assets[0]) return null;
    return buildResult(result.assets[0]);
  }

  return { pickFromCamera, pickFromGallery };
}
