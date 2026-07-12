import { View, Text } from "react-native";
import { StyleSheet } from "react-native-unistyles";
import { createText } from "@/styles/themeComponents";
import Button from "@/components/primatives/Button";
import { useThemeStore, ThemeName } from "@/styles/useThemeStore";

const THEME_OPTIONS: { label: string; value: ThemeName }[] = [
  { label: "Light", value: "light" },
  { label: "Dark", value: "dark" },
];

export default function ThemeSelector() {
  const theme = useThemeStore((s) => s.theme);
  const setTheme = useThemeStore((s) => s.setTheme);

  return (
    <View style={styles.row}>
      <Text style={styles.label}>Theme</Text>

      {THEME_OPTIONS.map((option) => (
        <Button
          key={option.value}
          label={option.label}
          buttonType="action"
          isSelected={theme === option.value}
          onPress={() => setTheme(option.value)}
        />
      ))}
    </View>
  );
}

const styles = StyleSheet.create((theme) => ({
  row: {
    alignItems: "center",
    flexDirection: "row",
    gap: theme.gap.control,
  },
  label: {
    color: theme.colors.text.primary,
    ...createText(theme, "header2"),
  },
}));
