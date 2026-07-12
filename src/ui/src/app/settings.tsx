import { useState, type ReactNode } from "react";
import { View, Text } from "react-native";
import { StyleSheet } from "react-native-unistyles";
import { createText, createContainer } from "@/styles/themeComponents";
import EndpointSelector from "@/components/EndpointSelector";
import ConfirmationModal from "@/components/modals/ConfirmationModal";
import Button from "@/components/primatives/Button";
import { useConfigStore } from "@/services/config/useConfigStore";
import { useThemeStore, ThemeName } from "@/styles/useThemeStore";

const THEME_OPTIONS: { label: string; value: ThemeName }[] = [
  { label: "Light", value: "light" },
  { label: "Dark", value: "dark" },
];

export default function SettingsScreen() {
  const restoreDefaults = useConfigStore((s) => s.restoreDefaults);
  const themeName = useThemeStore((s) => s.theme);
  const setTheme = useThemeStore((s) => s.setTheme);

  const [confirmVisible, setConfirmVisible] = useState(false);

  return (
    <View style={styles.column}>
      <SettingRow label="Server">
        <EndpointSelector />
      </SettingRow>

      <SettingRow label="Theme">
        {THEME_OPTIONS.map(({ label, value }) => (
          <Button
            key={value}
            label={label}
            buttonType="action"
            isSelected={themeName === value}
            onPress={() => setTheme(value)}
          />
        ))}
      </SettingRow>

      <SettingRow label="Restore">
        <Button
          label="Restore Defaults"
          buttonType="danger"
          onPress={() => setConfirmVisible(true)}
        />
      </SettingRow>

      <ConfirmationModal
        visible={confirmVisible}
        title="Restore Defaults"
        message="This will remove any custom server endpoints and restore the defaults. Continue?"
        onClose={() => setConfirmVisible(false)}
        onConfirm={() => {
          restoreDefaults();
          setConfirmVisible(false);
        }}
      />
    </View>
  );
}

/* Owns the layout for every settings entry: a card holding a label and its
   controls, so the child components only supply the controls themselves. */
function SettingRow({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <View style={styles.card}>
      <Text style={styles.label}>{label}</Text>
      <View style={styles.controls}>{children}</View>
    </View>
  );
}

const styles = StyleSheet.create((theme) => ({
  column: {
    gap: theme.gap.surface,
  },
  card: {
    ...createContainer(theme, "card"),
    flexDirection: "row",
    alignItems: "center",
  },
  label: {
    color: theme.colors.text.primary,
    width: 90,
    ...createText(theme, "header2"),
  },
  controls: {
    flex: 1,
    flexDirection: "row",
    alignItems: "center",
    gap: theme.gap.control,
  },
}));
