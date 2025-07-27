import { StyleSheet } from "react-native";

export const ModalStyles = StyleSheet.create({
  overlay: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  container: {  
    padding: 20,
    backgroundColor: 'white',
    borderRadius: 10,
    alignItems: 'center',
    boxShadow: '0px 4px 10px rgba(0, 0, 0, 0.25)',
  },  
});