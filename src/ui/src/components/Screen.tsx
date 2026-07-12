import type { ReactNode } from "react";
import { Text, View } from "react-native";
import { StyleSheet } from "react-native-unistyles";
import { createText } from "@/styles/themeComponents";

type ScreenProps = {
  title: string;
  children?: ReactNode;
};

export function Screen({ title, children }: ScreenProps) {
  return (
    <View style={styles.screen}>
      <Text style={styles.title}>{title}</Text>
      {children}
    </View>
  );
}

const styles = StyleSheet.create((theme) => ({
  /* Background/padding come from the layout's container. */
  screen: {
    flex: 1,
    gap: theme.gap.surface,
  },
  title: {
    color: theme.colors.text.primary,
    ...createText(theme, "header1"),
  },
}));
