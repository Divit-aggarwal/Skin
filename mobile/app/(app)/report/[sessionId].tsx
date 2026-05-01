import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useLocalSearchParams, router } from 'expo-router';
import { colors, typography } from '../../../constants/theme';

export default function ReportScreen() {
  const { sessionId } = useLocalSearchParams<{ sessionId: string }>();

  return (
    <View style={styles.container}>
      <Text style={styles.label}>Report</Text>
      <Text style={styles.id}>{sessionId}</Text>
      <TouchableOpacity style={styles.btn} onPress={() => router.replace('/(app)')}>
        <Text style={styles.btnText}>Back to Home</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  label: {
    fontSize: typography.fontSize.xxl,
    color: colors.textPrimary,
    fontWeight: '600',
    marginBottom: 8,
  },
  id: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    marginBottom: 32,
  },
  btn: {
    paddingHorizontal: 24,
    paddingVertical: 14,
    backgroundColor: colors.primary,
    borderRadius: 12,
  },
  btnText: {
    color: '#ffffff',
    fontSize: typography.fontSize.md,
    fontWeight: '600',
  },
});
