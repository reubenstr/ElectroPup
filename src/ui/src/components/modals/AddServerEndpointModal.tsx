import React, { useState, useEffect } from "react";
import { Modal, View, Text, TextInput, TouchableOpacity, StyleSheet, Pressable } from "react-native";
import { Server, Endpoint } from "@/services/config/configTypes";
import { ButtonStyles } from "@/src/styles/buttonStyles";
import { ModalStyles } from "@/src/styles/modalStyles";

interface ServerEndpointDialogProps {
  server: Server;
  operation: 'add' | 'edit';
  visible: boolean;
  onClose: () => void;
  onSubmit: (endpoint: Endpoint) => void;
}

export default function NetworkEndpointDialog({ server, operation, visible, onClose, onSubmit }: ServerEndpointDialogProps) {
  const [description, setDescription] = useState<string>('');
  const [address, setAddress] = useState<string>('');
  const [port, setPort] = useState<string>('');
  const [encypted, setEncrypted] = useState<boolean>(false);
  const [errors, setErrors] = useState<{ description?: string; address?: string; port?: string }>({});

  const [header, setHeader] = useState('');

  useEffect(() => {
    if (operation === 'add') {
      setHeader(`Add endpoint to ${server.name}`);
    } else if (operation === 'edit') {
      setHeader(`Edit endpoint on ${server.name}`);
      setDescription(server.selectedEndpoint.description);
      setAddress(server.selectedEndpoint.address);
      setPort(String(server.selectedEndpoint.port));
      setEncrypted(server.selectedEndpoint.encrypted)
    }
  }, [operation, server]);

  const handleSubmit = () => {
    let newErrors: { description?: string; address?: string; port?: string } = {};

    if (!description) newErrors.description = "Description is required.";
    if (!address) newErrors.address = "Address is required.";
    if (!port) newErrors.port = "Port is required.";

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    const newEndpoint: Endpoint = {
      description,
      address,
      port: parseInt(port, 10),
      encrypted: encypted
    };

    onSubmit(newEndpoint);
    onClose();
    setErrors({});
  };

  return (
    <Modal visible={visible} transparent animationType="fade">
      <View style={ModalStyles.overlay}>
        <View style={styles.dialog}>
          <Text style={styles.title}>{header}</Text>

          <View style={styles.inputContainer}>
            <TextInput
              style={styles.input}
              placeholder="Description"
              value={description}
              onChangeText={setDescription}
            />
            {errors.description && <Text style={styles.errorText}>{errors.description}</Text>}
          </View>

          <View style={styles.inputContainer}>
            <TextInput
              style={styles.input}
              placeholder="Address"
              value={address}
              onChangeText={setAddress}
            />
            {errors.address && <Text style={styles.errorText}>{errors.address}</Text>}
          </View>

          <View style={styles.inputContainer}>
            <TextInput
              style={styles.input}
              placeholder="Port"
              value={port}
              onChangeText={(text) => {
                const numericValue = text.replace(/[^0-9]/g, "");
                setPort(numericValue);
              }}
              keyboardType="numeric"
            />
            {errors.port && <Text style={styles.errorText}>{errors.port}</Text>}
          </View>

          <View style={CheckBoxStyles.container}>
            <Pressable style={CheckBoxStyles.checkboxContainer} onPress={() => setEncrypted(!encypted)}>
              <View style={[CheckBoxStyles.checkbox, encypted && CheckBoxStyles.checked]}>
                {encypted && <Text style={CheckBoxStyles.checkmark}>✓</Text>}
              </View>
              <Text style={CheckBoxStyles.label}>Encrypted</Text>
            </Pressable>
          </View>

          <View style={styles.buttonContainer}>
            <TouchableOpacity style={[ButtonStyles.button, ButtonStyles.cancel]} onPress={onClose}>
              <Text style={ButtonStyles.text}>Cancel</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[ButtonStyles.button, ButtonStyles.primary]} onPress={handleSubmit}>
              <Text style={ButtonStyles.text}>{operation === 'add' ? "Add" : "Apply"}</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  dialog: {
    width: "50%",
    backgroundColor: "#fff",
    padding: 20,
    borderRadius: 10,
    alignItems: "center",
  },
  title: {
    fontSize: 20,
    fontWeight: "bold",
    marginBottom: 15,
  },
  inputContainer: {
    width: "100%",
    marginBottom: 10,
  },
  input: {
    width: "100%",
    borderBottomWidth: 1,
    borderColor: "#ccc",
    padding: 10,
  },
  errorText: {
    color: "red",
    fontSize: 12,
    marginTop: 5,
  },
  buttonContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    width: "100%",
  },
});

const CheckBoxStyles = StyleSheet.create({
  container: {
    width: "100%",
    marginTop: 10,
    marginLeft: 10,
    marginBottom: 20,
  },
  checkboxContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  checkbox: {
    height: 24,
    width: 24,
    borderWidth: 2,
    borderColor: '#555',
    marginRight: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  checked: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
  },
  checkmark: {
    color: 'white',
    fontWeight: 'bold',
  },
  label: {
    fontSize: 16,
  },
});
