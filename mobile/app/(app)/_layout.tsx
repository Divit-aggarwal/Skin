import { View } from 'react-native';
import { Tabs, Redirect } from 'expo-router';
import { useAuthStore } from '../../store/authStore';

function HomeIcon({ color }: { color: string }) {
  return (
    <View style={{ width: 22, height: 20 }}>
      <View style={{
        position: 'absolute', top: 0, left: 1, right: 1,
        borderLeftWidth: 10, borderRightWidth: 10, borderBottomWidth: 9,
        borderLeftColor: 'transparent', borderRightColor: 'transparent',
        borderBottomColor: color,
      }} />
      <View style={{
        position: 'absolute', bottom: 0, left: 4, right: 4, height: 11,
        backgroundColor: color, borderTopLeftRadius: 1, borderTopRightRadius: 1,
      }} />
    </View>
  );
}

function ScanIcon({ color }: { color: string }) {
  return (
    <View style={{
      width: 20, height: 20, borderRadius: 5,
      borderWidth: 2, borderColor: color,
      alignItems: 'center', justifyContent: 'center',
    }}>
      <View style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: color }} />
    </View>
  );
}

function HistoryIcon({ color }: { color: string }) {
  return (
    <View style={{ width: 20, height: 18, justifyContent: 'space-between' }}>
      <View style={{ height: 2.5, backgroundColor: color, borderRadius: 1.5 }} />
      <View style={{ height: 2.5, backgroundColor: color, borderRadius: 1.5 }} />
      <View style={{ height: 2.5, backgroundColor: color, borderRadius: 1.5 }} />
    </View>
  );
}

function TwinIcon({ color }: { color: string }) {
  return (
    <View style={{ width: 20, height: 20, alignItems: 'center' }}>
      <View style={{ width: 9, height: 9, borderRadius: 4.5, backgroundColor: color, marginBottom: 2 }} />
      <View style={{
        width: 18, height: 9,
        borderTopLeftRadius: 9, borderTopRightRadius: 9,
        backgroundColor: color,
      }} />
    </View>
  );
}

export default function AppLayout() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  if (!isAuthenticated) {
    return <Redirect href="/login" />;
  }

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: '#0a0a0a',
        tabBarInactiveTintColor: '#aaaaaa',
        tabBarStyle: {
          backgroundColor: '#f8f7f4',
          borderTopColor: 'rgba(0,0,0,0.08)',
          borderTopWidth: 0.5,
        },
        tabBarLabelStyle: { fontSize: 10, fontWeight: '500' },
      }}
    >
      <Tabs.Screen
        name="scan"
        options={{
          title: 'Scan',
          tabBarIcon: ({ color }) => <ScanIcon color={color} />,
        }}
      />
      <Tabs.Screen
        name="history"
        options={{
          title: 'History',
          tabBarIcon: ({ color }) => <HistoryIcon color={color} />,
        }}
      />
      <Tabs.Screen
        name="twin"
        options={{
          title: 'Twin',
          tabBarIcon: ({ color }) => <TwinIcon color={color} />,
        }}
      />
      <Tabs.Screen
        name="index"
        options={{
          title: 'Profile',
          tabBarIcon: ({ color }) => <HomeIcon color={color} />,
        }}
      />
      <Tabs.Screen
        name="profile-setup"
        options={{
          href: null,
          tabBarStyle: { display: 'none' },
        }}
      />
      <Tabs.Screen
        name="report/[sessionId]"
        options={{
          href: null,
          tabBarStyle: { display: 'none' },
        }}
      />
    </Tabs>
  );
}
