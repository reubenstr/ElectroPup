import React, { useEffect, useState, useRef } from "react";
import { StatusBar } from 'expo-status-bar';
import { Text, View, StyleSheet, TouchableOpacity } from 'react-native';
import { Link } from 'expo-router';
import Icon from 'react-native-vector-icons/FontAwesome';
import { useConfigStore } from '@/services/config/useConfigStore'
import ServerSelector from '@/components/ServerSelector';
import ConfirmationModal from '../components/modals/ConfirmationModal'
import { ControlStyles, ButtonStyles, IconStyles } from "@/styles/buttonStyles";
import colors from "@/styles/colors";


export default function ConfigScreen() {
  const configStore = useConfigStore();

  const [displayConfirmationModal, setDisplayConfirmationModal] = useState(false);

  const restoreDefaults = () => {
    setDisplayConfirmationModal(false);
    configStore.restoreDefaults();
  }

  return (
    <View style={styles.container}>
      <View style={styles.innerContainer}>
        <ConfirmationModal
          visible={displayConfirmationModal}
          message="Are you sure you want to restore all settings to default?"
          onCancel={() => setDisplayConfirmationModal(false)}
          onConfirm={restoreDefaults}
        />
        <View style={styles.column}>
          <Text style={styles.header}>Servers</Text>
          <ServerSelector />
          <Text style={styles.header}>System</Text>
          <View style={styles.row}>
          
            <TouchableOpacity
              style={[IconStyles.container, ControlStyles.primary]}
              onPress={() => setDisplayConfirmationModal(true)}
            >             
                <Text style={styles.label}>Restore Defaults</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 20,
  },
  innerContainer: {
    width: '100%',
    maxWidth: 800,
    paddingHorizontal: 10,
  },
  column: {
    flexDirection: 'column',
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 5,
    marginVertical: 5,
    marginHorizontal: 0,
    backgroundColor: '#999',
    borderRadius: 5
  },
  header: {
    fontSize: 20,
    fontWeight: "bold",
    textAlign: 'center',
    color: '#ddd'
  },
  label: {
    fontSize: 14,
    fontWeight: "bold",
    color: colors.dark.text
  },
});
