import { useEffect, useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { Redirect } from 'expo-router';
import { useAuthStore } from '../store/authStore';
import { colors } from '../constants/theme';

export default function Index() {
  const [hydrated, setHydrated] = useState(false);
  const hydrate = useAuthStore((s) => s.hydrate);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  useEffect(() => {
    hydrate().finally(() => setHydrated(true));
  }, [hydrate]);

  if (!hydrated) {
    return <View style={styles.container} />;
  }

  return <Redirect href={isAuthenticated ? '/(app)/' : '/login'} />;
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
});
