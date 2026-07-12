import { Image, Linking, Pressable, Text, View } from "react-native";
import { StyleSheet } from "react-native-unistyles";
import { createText, createShadow } from "@/styles/themeComponents";

const GITHUB_URL = "https://github.com/reubenstr/ElectroPup/";

/* electropup.png's native pixel size; Image doesn't reliably honor
   `aspectRatio` for scaling a local asset, so height is computed directly. */
const LOGO_WIDTH = 640;
const LOGO_HEIGHT = LOGO_WIDTH * (1161 / 2132);

export default function AboutScreen() {
  return (
    <View style={styles.screen}>
      <Image
        source={require("@/assets/images/electropup.png")}
        style={styles.logo}
        resizeMode="contain"
      />

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
  );
}

const styles = StyleSheet.create((theme) => ({
  screen: {
    flex: 1,
    alignItems: "center",
    gap: theme.gap.surface,
    padding: theme.padding.surface,
  },
  logo: {
    width: LOGO_WIDTH,
    height: LOGO_HEIGHT,
    borderWidth: theme.borderWidth.card,
    borderColor: theme.colors.border.card,
    borderRadius: theme.radius.card,
    overflow: "hidden",
    ...createShadow(theme, "large"),
  },
  title: {
    color: theme.colors.text.primary,
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
