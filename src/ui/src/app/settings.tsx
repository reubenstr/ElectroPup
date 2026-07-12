import EndpointSelector from "@/components/EndpointSelector";
import ThemeSelector from "@/components/ThemeSelector";
import { View } from "react-native";
import { StyleSheet } from "react-native-unistyles";

export default function SettingsScreen() {
  return (
    <View style={styles.column}>
      <EndpointSelector />
      <ThemeSelector />
    </View>
  );
}

const styles = StyleSheet.create((theme) => ({
  column: {
    gap: theme.gap.surface,
  },
}));
