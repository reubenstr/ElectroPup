import { Image, Linking, Pressable, Text, View } from "react-native";
import { StyleSheet } from "react-native-unistyles";
import { createText, createShadow } from "@/styles/themeComponents";

const GITHUB_URL = "https://github.com/reubenstr/ElectroPup/";
const LOGO_WIDTH = 640;
const LOGO_HEIGHT = LOGO_WIDTH * (1161 / 2132);

export default function AboutScreen() {
  return (
    <View style={styles.container}>

      <Image
        source={require("@/assets/images/electropup.png")}
        style={styles.logo}
        resizeMode="contain"
      />

      <View style={styles.body}>
        <Text style={styles.title}>ElectroPup</Text>

        <Text style={styles.description}>
          This app is an interactive GUI for ploting ElectroPup&apos;s live and simulated positions as well as provide live status of various subsystems.</Text>

        <Pressable
          accessibilityRole="link"
          onPress={() => Linking.openURL(GITHUB_URL)}
        >
          <Text style={styles.link}>{GITHUB_URL}</Text>
        </Pressable>
      </View>

    </View>
  );
}

const styles = StyleSheet.create((theme) => ({
  container: {
    flex: 1,
    alignItems: "center",
    gap: theme.gap.surface,
    padding: theme.padding.surface,
  },
  logo: {
    flex: 1,
    maxWidth: LOGO_WIDTH,
    maxHeight: LOGO_HEIGHT,
    borderWidth: theme.borderWidth.card,
    borderColor: theme.colors.border.card,
    borderRadius: theme.radius.card,
    overflow: "hidden",
    ...createShadow(theme, "large"),
  },
  body: {
    flex: 1,
    alignItems: "center",
    gap: 20,
  },
  title: {
    color: theme.colors.text.primary,
    textAlign: "center",
    ...createText(theme, "header1"),
  },
  description: {
    color: theme.colors.text.secondary,
    textAlign: "center",
    maxWidth: 640,
    ...createText(theme, "body"),
  },
  link: {
    color: theme.colors.text.action,
    ...createText(theme, "body"),
    textDecorationLine: "underline",
  },
}));
