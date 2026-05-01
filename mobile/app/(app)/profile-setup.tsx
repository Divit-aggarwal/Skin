import { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  ActivityIndicator,
} from 'react-native';
import { router } from 'expo-router';
import { useUpdateProfile } from '../../hooks/useProfile';
import { useUserStore } from '../../store/userStore';
import { SkinType } from '../../api/users';
import { colors, typography, spacing, radius } from '../../constants/theme';

const SKIN_TYPES: { label: string; value: SkinType }[] = [
  { label: 'Normal', value: 'normal' },
  { label: 'Oily', value: 'oily' },
  { label: 'Dry', value: 'dry' },
  { label: 'Combination', value: 'combination' },
  { label: 'Sensitive', value: 'sensitive' },
];

export default function ProfileSetupScreen() {
  const [displayName, setDisplayName] = useState('');
  const [age, setAge] = useState('');
  const [skinType, setSkinType] = useState<SkinType | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);

  const markProfileSetupSeen = useUserStore((s) => s.markProfileSetupSeen);
  const { mutateAsync, isPending } = useUpdateProfile();

  const handleSave = async () => {
    if (!skinType) {
      setApiError('Please select your skin type to continue.');
      return;
    }
    setApiError(null);
    try {
      await mutateAsync({
        display_name: displayName.trim() || undefined,
        age: age ? parseInt(age, 10) : undefined,
        skin_type: skinType,
      });
      markProfileSetupSeen();
      router.replace('/(app)/');
    } catch {
      setApiError('Failed to save profile. Please try again.');
    }
  };

  const handleSkip = () => {
    markProfileSetupSeen();
    router.replace('/(app)/');
  };

  return (
    <KeyboardAvoidingView
      style={styles.flex}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
        <View style={styles.inner}>
          <Text style={styles.title}>Your skin profile</Text>
          <Text style={styles.subtitle}>Helps us personalise your analysis</Text>

          {apiError && (
            <View style={styles.errorBanner}>
              <Text style={styles.errorText}>{apiError}</Text>
            </View>
          )}

          <View style={styles.field}>
            <Text style={styles.label}>NAME (OPTIONAL)</Text>
            <TextInput
              style={styles.input}
              placeholder="Your name"
              placeholderTextColor={colors.textTertiary}
              autoCapitalize="words"
              value={displayName}
              onChangeText={setDisplayName}
            />
          </View>

          <View style={styles.field}>
            <Text style={styles.label}>AGE (OPTIONAL)</Text>
            <TextInput
              style={styles.input}
              placeholder="Your age"
              placeholderTextColor={colors.textTertiary}
              keyboardType="number-pad"
              maxLength={3}
              value={age}
              onChangeText={(t) => setAge(t.replace(/[^0-9]/g, ''))}
            />
          </View>

          <View style={styles.field}>
            <Text style={styles.label}>SKIN TYPE</Text>
            <View style={styles.pillRow}>
              {SKIN_TYPES.map((item) => {
                const selected = skinType === item.value;
                return (
                  <TouchableOpacity
                    key={item.value}
                    style={[styles.pill, selected && styles.pillSelected]}
                    onPress={() => setSkinType(item.value)}
                  >
                    <Text style={[styles.pillText, selected && styles.pillTextSelected]}>
                      {item.label}
                    </Text>
                  </TouchableOpacity>
                );
              })}
            </View>
          </View>

          <TouchableOpacity
            style={[styles.button, isPending && styles.buttonDisabled]}
            onPress={handleSave}
            disabled={isPending}
          >
            {isPending ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Save and continue</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity style={styles.skipButton} onPress={handleSkip}>
            <Text style={styles.skipText}>Skip for now</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.background },
  scroll: { flexGrow: 1 },
  inner: {
    flex: 1,
    paddingHorizontal: spacing[6],
    paddingTop: spacing[16],
    paddingBottom: spacing[8],
  },
  title: {
    fontSize: typography.fontSize.xxl,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing[1],
  },
  subtitle: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
    marginBottom: spacing[8],
  },
  errorBanner: {
    backgroundColor: '#FEE2E2',
    borderRadius: radius.md,
    padding: spacing[3],
    marginBottom: spacing[4],
  },
  errorText: { color: colors.danger, fontSize: typography.fontSize.sm },
  field: { marginBottom: spacing[5] },
  label: {
    fontSize: typography.fontSize.sm,
    fontWeight: '500',
    color: colors.textSecondary,
    marginBottom: 6,
    letterSpacing: 0.5,
  },
  input: {
    backgroundColor: colors.surface,
    borderRadius: 14,
    borderWidth: 0.5,
    borderColor: 'rgba(0,0,0,0.12)',
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 15,
    color: colors.textPrimary,
  },
  pillRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing[2],
  },
  pill: {
    paddingHorizontal: 14,
    paddingVertical: 9,
    borderRadius: radius.full,
    borderWidth: 0.5,
    borderColor: 'rgba(0,0,0,0.12)',
    backgroundColor: colors.surface,
  },
  pillSelected: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  pillText: {
    fontSize: typography.fontSize.md,
    color: colors.textPrimary,
    fontWeight: '500',
  },
  pillTextSelected: { color: '#fff' },
  button: {
    backgroundColor: colors.primary,
    borderRadius: radius.lg,
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: spacing[4],
  },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: '#fff', fontSize: 15, fontWeight: '500' },
  skipButton: {
    alignItems: 'center',
    paddingVertical: spacing[4],
    marginTop: spacing[2],
  },
  skipText: {
    fontSize: typography.fontSize.md,
    color: colors.textSecondary,
  },
});
