import "@/styles/unistylesConfig";
import { useEffect } from "react";
import { useFonts } from "expo-font";
import { Stack, SplashScreen, ThemeProvider, DefaultTheme } from "expo-router";
import { View } from "react-native";
import { TopNav } from "@/components/TopNav";
import { StyleSheet } from "react-native-unistyles";
import { createShadow } from "@/styles/themeComponents";
import { useData } from "@/services/data/useData";

SplashScreen.preventAutoHideAsync();

const navigationTheme = {
  ...DefaultTheme,
  colors: { ...DefaultTheme.colors, background: "transparent" },
};

export default function RootLayout() {
  
  // Keys must match the fontFamily names used in the theme's typography.
  const [fontsLoaded, fontError] = useFonts({
    OrbitronRegular: require("@/assets/fonts/orbitron/static/Orbitron-Regular.ttf"),
    OrbitronMedium: require("@/assets/fonts/orbitron/static/Orbitron-Medium.ttf"),
    OrbitronBold: require("@/assets/fonts/orbitron/static/Orbitron-Bold.ttf"),
  });

  useEffect(() => {
    if (fontsLoaded || fontError) {
      SplashScreen.hideAsync();
    }
  }, [fontsLoaded, fontError]);

  /* Single owner of the socket for the whole app; screens read useDataStore.
     Must stay above the early return to keep hook order stable. */
  useData();

  if (!fontsLoaded && !fontError) {
    return null;
  }

  return (
    <View style={styles.root}>
      <View style={styles.column}>
        <TopNav />
        <View style={styles.container}>
          <ThemeProvider value={navigationTheme}>
            <Stack screenOptions={{ headerShown: false }} />
          </ThemeProvider>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create((theme, rt) => ({
  root: {
    flex: 1,
    alignItems: "center",
    paddingTop: theme.padding.surface + rt.insets.top,
    paddingBottom: theme.padding.surface + rt.insets.bottom,
    paddingLeft: theme.padding.surface + rt.insets.left,
    paddingRight: theme.padding.surface + rt.insets.right,
    backgroundColor: theme.colors.background.inset,
  },
  column: {
    flex: 1,
    width: "100%",
    maxWidth: theme.size.content.maxWidth,
    gap: theme.gap.surface,
  },
  container: {
    flex: 1,
    overflow: "hidden",
    padding: theme.padding.surface,
    backgroundColor: theme.colors.background.surface,
    borderWidth: theme.borderWidth.surface,
    borderColor: theme.colors.border.surface,
    borderRadius: theme.radius.surface,
    ...createShadow(theme, "medium"),
  },
}));
