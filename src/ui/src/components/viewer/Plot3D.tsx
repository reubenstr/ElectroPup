import { View, Text } from "react-native";
import { StyleSheet } from "react-native-unistyles";
import { createText } from "@/styles/themeComponents";
import { Data } from "@/services/data/dataTypes";

interface Plot3DProps {
  data?: Data;
}

export default function Plot3D(_props: Plot3DProps) {
  return (
    <View style={styles.container}>
      <Text style={styles.error}>Plot not supported on native platform.</Text>
    </View>
  );
}

const styles = StyleSheet.create((theme) => ({
  container: {
    flex: 1,
    width: "100%",
    alignItems: "center",
    justifyContent: "center",
  },
  error: {
    color: theme.colors.text.error,
    ...createText(theme, "body"),
  },
}));
