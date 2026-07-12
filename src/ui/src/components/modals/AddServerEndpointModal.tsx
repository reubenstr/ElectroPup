import { useState, useEffect } from "react";
import { Modal, View, Text, TextInput } from "react-native";
import { StyleSheet, useUnistyles } from "react-native-unistyles";
import {
  overlayStyles,
  modalStyles,
  createText,
  inputStyles,
} from "@/styles/themeComponents";
import { Endpoint } from "@/services/config/configTypes";
import Button from "@/components/primatives/Button";

interface AddServerEndpointModalProps {
  operation: "add" | "edit";
  endpoint?: Endpoint;
  visible: boolean;
  onClose: () => void;
  onSubmit: (endpoint: Endpoint) => void;
}

type Errors = {
  description?: string;
  address?: string;
  port?: string;
};

export default function AddServerEndpointModal({
  operation,
  endpoint,
  visible,
  onClose,
  onSubmit,
}: AddServerEndpointModalProps) {
  const { theme } = useUnistyles();

  const [description, setDescription] = useState("");
  const [address, setAddress] = useState("");
  const [port, setPort] = useState("");
  const [errors, setErrors] = useState<Errors>({});

  /* Seed the fields each time the modal opens. */
  useEffect(() => {
    if (!visible) return;

    const editing = operation === "edit";
    setDescription(editing ? (endpoint?.description ?? "") : "");
    setAddress(editing ? (endpoint?.address ?? "") : "");
    setPort(editing ? String(endpoint?.port ?? "") : "");
    setErrors({});
  }, [visible, operation, endpoint]);

  const handleSubmit = () => {
    const newErrors: Errors = {};

    if (!description) newErrors.description = "Description is required.";
    if (!address) newErrors.address = "Address is required.";
    if (!port) newErrors.port = "Port is required.";

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    onSubmit({ description, address, port: parseInt(port, 10) });
    onClose();
    setErrors({});
  };

  return (
    <Modal
      visible={visible}
      transparent
      statusBarTranslucent
      animationType="fade"
    >
      <View style={overlayStyles.overlay}>
        <View style={[modalStyles.container, styles.container]}>
          <Text style={styles.title}>
            {operation === "add" ? "Add endpoint" : "Edit endpoint"}
          </Text>

          <TextInput
            style={inputStyles.input}
            placeholder="Description"
            placeholderTextColor={theme.colors.text.disabled}
            value={description}
            onChangeText={setDescription}
          />
          {errors.description && (
            <Text style={styles.errorText}>{errors.description}</Text>
          )}

          <TextInput
            style={inputStyles.input}
            placeholder="Address"
            placeholderTextColor={theme.colors.text.disabled}
            value={address}
            onChangeText={setAddress}
          />
          {errors.address && (
            <Text style={styles.errorText}>{errors.address}</Text>
          )}

          <TextInput
            style={inputStyles.input}
            placeholder="Port"
            placeholderTextColor={theme.colors.text.disabled}
            value={port}
            onChangeText={(text) => setPort(text.replace(/[^0-9]/g, ""))}
            keyboardType="numeric"
          />
          {errors.port && <Text style={styles.errorText}>{errors.port}</Text>}

          <View style={styles.buttonRow}>
            <Button buttonType="info" label="Cancel" onPress={onClose} />
            <Button
              buttonType="action"
              label={operation === "add" ? "Add" : "Apply"}
              onPress={handleSubmit}
            />
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create((theme) => ({
  container: {
    width: 400,
  },
  title: {
    color: theme.colors.text.primary,
    ...createText(theme, "header1"),
  },
  errorText: {
    color: theme.colors.text.danger,
    fontSize: 12,
  },
  buttonRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: 10,
  },
}));
