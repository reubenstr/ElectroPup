import { Modal, View, Text, TouchableWithoutFeedback } from "react-native";
import { StyleSheet } from "react-native-unistyles";
import {
  createText,
  overlayStyles,
  modalStyles,
} from "@/styles/themeComponents";
import Button from "@/components/primatives/Button";

interface ModalProps {
  visible: boolean;
  title?: string;
  message: string;
  onConfirm: () => void;
  onClose: () => void;
}

export default function ConfirmationModal({
  visible,
  title = "Confirmation",
  message,
  onConfirm,
  onClose,
}: ModalProps) {
  return (
    <Modal
      transparent
      statusBarTranslucent
      visible={visible}
      animationType="fade"
      navigationBarTranslucent
    >
      <View style={overlayStyles.overlay}>
        <TouchableWithoutFeedback onPress={onClose}>
          <View style={StyleSheet.absoluteFill} />
        </TouchableWithoutFeedback>
        <View style={modalStyles.container}>
          <View style={styles.titleRow}>
            <Text style={styles.titleText}>{title}</Text>
          </View>
          <View style={styles.bodyRow}>
            <Text style={styles.bodyText}>{message}</Text>
          </View>
          <View style={styles.bottomRow}>
            <Button buttonType="info" label="Cancel" onPress={onClose} />
            <Button buttonType="danger" label="Confirm" onPress={onConfirm} />
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create((theme) => ({
  titleRow: {
    flexDirection: "row",
    alignItems: "center",
    minHeight: 40,
    paddingBottom: theme.padding.card,
    borderBottomWidth: theme.borderWidth.divider,
    borderBottomColor: theme.colors.divider,
  },
  titleText: {
    color: theme.colors.text.primary,
    ...createText(theme, "header2"),
  },
  bodyRow: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  bodyText: {
    color: theme.colors.text.primary,
    ...createText(theme, "body"),
  },
  bottomRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    minHeight: 40,
    paddingTop: theme.padding.card,
    borderTopWidth: theme.borderWidth.divider,
    borderTopColor: theme.colors.divider,
  },
}));
