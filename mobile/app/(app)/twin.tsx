import { View, Text, StyleSheet } from 'react-native';
import { colors, typography } from '../../constants/theme';

export default function TwinScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Digital Twin — placeholder</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: colors.background },
  text: { fontSize: typography.fontSize.lg, color: colors.textPrimary },
});
