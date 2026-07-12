import { useState } from "react";
import { ScrollView, Text, View } from "react-native";
import { StyleSheet, useUnistyles } from "react-native-unistyles";
import * as Clipboard from "expo-clipboard";
import { createText, createContainer } from "@/styles/themeComponents";
import { useDataStore, ConnectionStatus } from "@/services/data/useDataStore";
import { useConfigStore } from "@/services/config/useConfigStore";
import {
  generateUrl,
  selectedEndpoint,
} from "@/services/config/configUtilities";
import Button from "@/components/primatives/Button";

const COPIED_LABEL_MS = 1500;

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

  const [copied, setCopied] = useState(false);

  const statusColor: Record<ConnectionStatus, string> = {
    connected: theme.colors.text.success,
    connecting: theme.colors.text.warning,
    disconnected: theme.colors.text.error,
  };

  const handleCopy = async () => {
    if (!data) return;
    await Clipboard.setStringAsync(JSON.stringify(data, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), COPIED_LABEL_MS);
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

        <View style={styles.copyButton}>
          <Button
            label={copied ? "Copied" : "Copy"}
            iconName={copied ? "check" : undefined}
            buttonType="action"
            disabled={!data}
            onPress={handleCopy}
          />
        </View>
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
  copyButton: {
    marginLeft: "auto",
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
