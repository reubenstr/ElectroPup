import { useEffect } from 'react';
import { Platform, StyleSheet, View, Text, TouchableOpacity } from 'react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as ScreenOrientation from 'expo-screen-orientation';
import { useNavigation, useNavigationState } from '@react-navigation/native';
import { useFonts } from 'expo-font';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import 'react-native-reanimated';
import * as NavigationBar from 'expo-navigation-bar';
import { useConfigStore } from '@/services/config/useConfigStore';
import { Ionicons } from '@expo/vector-icons';

export default function RootLayout() {
  const [loaded] = useFonts({
    SpaceMono: require('../assets/fonts/SpaceMono-Regular.ttf'),
  });

  useEffect(() => {
    if (Platform.OS === 'android') {
      const lockOrientation = async () => {
        await ScreenOrientation.lockAsync(ScreenOrientation.OrientationLock.LANDSCAPE);
      };
      lockOrientation();
    }
  }, []);

  const AndroidSoftwareNavHidden = async () => {
    console.log("AndroidSoftwareNavHidden")
    await NavigationBar.setPositionAsync('absolute')
    await NavigationBar.setVisibilityAsync("hidden");
    await NavigationBar.setBehaviorAsync('overlay-swipe')
    await NavigationBar.setBackgroundColorAsync("ffffff00");
    await NavigationBar.setButtonStyleAsync("dark");
  }

  useEffect(() => {
    if (Platform.OS === 'android') {
      AndroidSoftwareNavHidden()
    }
  }, [])

  const loadStore = useConfigStore(state => state.loadStore);
  useEffect(() => {
    loadStore();
  }, []);

  if (!loaded) {
    // Async font loading only occurs in development.
    return null;
  }

  const Header = ({ title }: { title: string }) => {
    const navigation = useNavigation();
    const routesLength = useNavigationState(state => state.routes.length);
    const isRoot = routesLength <= 1;
    return (
      <View style={headerStyles.container}>
        <TouchableOpacity
          onPress={() => {
            if (!isRoot) {
              navigation.goBack();
            } else {
              (navigation as any).navigate('index');
            }
          }}
        >
          <Ionicons
            name={isRoot ? 'home' : 'arrow-back'}
            size={30}
            color="#333"
          />
        </TouchableOpacity>
        <Text style={headerStyles.title}>{title}</Text>
      </View>
    );
  };

  return (
    <GestureHandlerRootView style={styles.gestureHander}>
      <SafeAreaView
        style={styles.safeArea}
        edges={[]}
      >
        <StatusBar style="auto" hidden />
        <Stack screenOptions={{ contentStyle: styles.screen }}>
          <Stack.Screen name="index" options={{ headerShown: false }} />
          <Stack.Screen
            name="config"
            options={{
              headerShown: true,
              header: () => <Header title="Configuration" />,
            }}
          />
           <Stack.Screen
            name="data"
            options={{
              headerShown: true,
              header: () => <Header title="Quad Data" />,
            }}
          />
          <Stack.Screen name="+not-found" />
        </Stack>
      </SafeAreaView>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  gestureHander: {
    flex: 1,
    backgroundColor: '#00ff00',
  },
  safeArea: {
    flex: 1,
    backgroundColor: 'transparent',
  },
  screen: {
    backgroundColor: '#333333',
  }
});

const headerStyles = StyleSheet.create({
  container: {
    height: 60,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    backgroundColor: '#999',
    borderBottomColor: '#555555'
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#000',
    marginLeft: 12,
  },
});
