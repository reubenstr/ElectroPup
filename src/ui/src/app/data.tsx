import { ScrollView, Text, View } from "react-native";
import { StyleSheet, useUnistyles } from "react-native-unistyles";
import { createText, createContainer } from "@/styles/themeComponents";
import { useDataStore, ConnectionStatus } from "@/services/data/useDataStore";
import { useConfigStore } from "@/services/config/useConfigStore";
import {
  generateUrl,
  selectedEndpoint,
} from "@/services/config/configUtilities";

const STATUS_LABEL: Record<ConnectionStatus, string> = {
  connected: "Connected",
  connecting: "Connecting",
  disconnected: "Disconnected",
};

export default function DataScreen() {
  const { theme } = useUnistyles();

  const data = useDataStore((state) => state.data);
  const status = useDataStore((state) => state.status);
  const endpoint = useConfigStore((state) => selectedEndpoint(state.config));

  const statusColor: Record<ConnectionStatus, string> = {
    connected: theme.colors.text.success,
    connecting: theme.colors.text.warning,
    disconnected: theme.colors.text.error,
  };

  return (
    <View style={styles.screen}>
      <View style={styles.statusRow}>
        <View
          style={[styles.indicator, { backgroundColor: statusColor[status] }]}
        />
        <Text style={[styles.status, { color: statusColor[status] }]}>
          {STATUS_LABEL[status]}
        </Text>
        <Text style={styles.endpoint}>
          {endpoint ? generateUrl(endpoint) : "No endpoint selected"}
        </Text>
      </View>

      <ScrollView style={styles.viewer} contentContainerStyle={styles.content}>
        {data ? (
          <Text style={styles.json} selectable>
            {JSON.stringify(data, null, 2)}
          </Text>
        ) : (
          <Text style={styles.placeholder}>Waiting for data...</Text>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create((theme) => ({
  screen: {
    flex: 1,
    gap: theme.gap.surface,
  },
  statusRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: theme.gap.control,
    paddingLeft: 5,
  },
  indicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
  },
  status: {
    ...createText(theme, "header2"),
  },
  endpoint: {
    color: theme.colors.text.secondary,
    ...createText(theme, "secondary"),
  },
  viewer: {
    flex: 1,
    ...createContainer(theme, "inset"),
  },
  /* The JSON is wider than the screen, so let it scroll rather than wrap. */
  content: {
    flexGrow: 1,
  },
  json: {
    color: theme.colors.text.primary,
    ...createText(theme, "mono"),
  },
  placeholder: {
    color: theme.colors.text.secondary,
    ...createText(theme, "body"),
  },
}));
