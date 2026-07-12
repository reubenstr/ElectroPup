import { useState } from "react";
import { View, Text } from "react-native";
import { StyleSheet, useUnistyles } from "react-native-unistyles";
import { createText } from "@/styles/themeComponents";
import AddServerEndpointModal from "@/components/modals/AddServerEndpointModal";
import ConfirmationModal from "@/components/modals/ConfirmationModal";
import Button from "@/components/primatives/Button";
import Picker from "@/components/primatives/Picker";
import { Endpoint } from "@/services/config/configTypes";
import { generateUrl } from "@/services/config/configUtilities";
import { useConfigStore } from "@/services/config/useConfigStore";

export default function EndpointSelector() {
  const { theme } = useUnistyles();

  const config = useConfigStore((s) => s.config);
  const setSelection = useConfigStore((s) => s.setSelection);
  const addEndpoint = useConfigStore((s) => s.addEndpoint);
  const updateEndpoint = useConfigStore((s) => s.updateEndpoint);
  const removeEndpoint = useConfigStore((s) => s.removeEndpoint);

  const [operation, setOperation] = useState<"add" | "edit">("add");
  const [displayEndpointModal, setDisplayEndpointModal] = useState(false);
  const [displayConfirmationModal, setDisplayConfirmationModal] =
    useState(false);

  const { endpoints, selection } = config;
  const selected = endpoints[selection];

  const handleEndpointChange = (address: string) => {
    const index = endpoints.findIndex((ep) => ep.address === address);
    setSelection(index >= 0 ? index : 0);
  };

  const handleSubmit = (endpoint: Endpoint) => {
    if (operation === "add") {
      addEndpoint(endpoint);
    } else {
      updateEndpoint(selection, endpoint);
    }
  };

  const handleRemove = () => {
    removeEndpoint(selection);
    setDisplayConfirmationModal(false);
  };

  return (
    <View style={styles.row}>
      <AddServerEndpointModal
        operation={operation}
        endpoint={operation === "edit" ? selected : undefined}
        visible={displayEndpointModal}
        onClose={() => setDisplayEndpointModal(false)}
        onSubmit={handleSubmit}
      />
      <ConfirmationModal
        visible={displayConfirmationModal}
        message="Are you sure you want to delete this endpoint?"
        onClose={() => setDisplayConfirmationModal(false)}
        onConfirm={handleRemove}
      />

      <Text style={styles.label}>Server</Text>

      <Picker
        selectedValue={selected?.address}
        onValueChange={handleEndpointChange}
        dropdownIconColor={theme.colors.text.primary}
        mode="dropdown"
      >
        {endpoints.map((endpoint, i) => (
          <Picker.Item
            key={i}
            label={`${endpoint.description} @ ${generateUrl(endpoint)}`}
            value={endpoint.address}
            color={theme.colors.text.primary}
          />
        ))}
      </Picker>

      <Button
        buttonType="action"
        iconName="add"
        onPress={() => {
          setOperation("add");
          setDisplayEndpointModal(true);
        }}
      />
      <Button
        buttonType="action"
        iconName="edit"
        disabled={!selected}
        onPress={() => {
          setOperation("edit");
          setDisplayEndpointModal(true);
        }}
      />
      <Button
        buttonType="danger"
        iconName="delete"
        disabled={!selected}
        onPress={() => setDisplayConfirmationModal(true)}
      />
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
