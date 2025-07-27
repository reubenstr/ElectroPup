import React, { useState, useEffect } from "react";
import { View, TextInput, TouchableOpacity, Text, StyleSheet } from "react-native";
import { useDataTransfer } from "@/services/useDataTransfer";

export default function DataScreen() {
  const { hexData, connected } = useDataTransfer();

  const [displayString, setDisplayString] = useState<string>("No data...");
  const [allowUpdates, setAllowUpdates] = useState(true);
  const [count, setCount] = useState<number>(0);

  useEffect(() => {
    if (hexData && allowUpdates) {
      const jsonString = JSON.stringify(hexData, null, 4)
      setDisplayString(jsonString)
      setCount(jsonString.replace(/[\t\r\n]/g, '').length)
    }
  }, [hexData]);

  const onSetPause = () => {
    setAllowUpdates(!allowUpdates);
  };

  return (
    <View style={styles.container}>
      <View style={styles.row}>
        <Text style={styles.statusText}>
          Hexapod: {connected ? "Connected" : "Disconnected"}
        </Text>
        <Text style={styles.statusText}>
       Character count: {count}
        </Text>
      </View>

      <TextInput
        style={styles.input}
        value={displayString}
        multiline
        scrollEnabled
      />

      <TouchableOpacity style={styles.button} onPress={onSetPause}>
        <Text style={styles.buttonText}>{allowUpdates ? "Pause" : "Resume"}</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    justifyContent: "flex-start",
  },
  row: {
    marginBottom: 10,
  },
  statusText: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#ccc",
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: "#ccc",
    borderRadius: 3,
    padding: 10,
    fontSize: 16,
    textAlignVertical: "top",
    marginBottom: 20,
    color: "#ccc",
  },
  button: {
    backgroundColor: "#4CAF50",
    padding: 10,
    borderRadius: 5,
    alignItems: "center",
  },
  buttonText: {
    color: "#fff",
    fontSize: 16,
  },
});
