import React from 'react';
import { Modal, View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { ButtonStyles } from "@/src/styles/buttonStyles";
import { ModalStyles } from "@/src/styles/modalStyles";

interface ConfirmationModalProps {
  visible: boolean;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}

const ConfirmationModal: React.FC<ConfirmationModalProps> = ({ visible, message, onConfirm, onCancel }) => {
  return (
    <Modal transparent visible={visible} animationType="fade">
      <View style={ModalStyles.overlay}>
        <View style={[ModalStyles.container, styles.modalContainer]}>
          <Text style={styles.message}>{message}</Text>
          <View style={styles.buttonContainer}>
            <TouchableOpacity style={[ButtonStyles.button, ButtonStyles.cancel]} onPress={onCancel}>
              <Text style={ButtonStyles.text}>Cancel</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[ButtonStyles.button, ButtonStyles.danger]} onPress={onConfirm}>
              <Text style={ButtonStyles.text}>Yes</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
};

export const styles = StyleSheet.create({
  modalContainer: {
    width: 300,
  },
  message: {
    fontSize: 18,
    textAlign: 'center',
    marginBottom: 20,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
  },
});

export default ConfirmationModal;
