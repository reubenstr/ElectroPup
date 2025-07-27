import React, { useRef, useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { DataTable } from 'react-native-paper';
import { motorAbbreviationToNameMap } from '@/constants/motorNames';
import { useDataTransfer } from '@/services/useDataTransfer';

export default function MotorTable() {

    const { hexData } = useDataTransfer();

    if (!hexData) {
        return (
            <></>
        )
    }

      const getMotor = (motorName: string) => {
        if (hexData?.motors && motorName in hexData?.motors) {
            return hexData.motors[motorName]
        }
    }

    return (
        <DataTable style={styles.container}>
            <DataTable.Header style={styles.header}>
                {['Motor', 'Enabled', 'Comms', 'Pos.', 'Fault', 'Position', 'Target Pos.', 'Velocity', 'Torque', 'Temperature'].map((title, index) => (
                    <DataTable.Title key={index} style={styles.title}>
                        <Text style={styles.text}>{title}</Text>
                    </DataTable.Title>
                ))}
            </DataTable.Header>
            <ScrollView contentContainerStyle={styles.scrollContainer}>
                {Object.entries(motorAbbreviationToNameMap).map(([key, value]) => {

                    const motor = getMotor(value)
                    return (
                        <DataTable.Row key={key} style={styles.row}>
                            <DataTable.Cell style={styles.cell}>
                                {key}
                            </DataTable.Cell>
                            <DataTable.Cell style={styles.cell}>
                                {motor?.values.enabled ? "✅" : "❌"}
                            </DataTable.Cell>
                            <DataTable.Cell style={styles.cell}>
                                {motor?.errors.communications ? "✅" : "❌"}
                            </DataTable.Cell>
                            <DataTable.Cell style={styles.cell}>
                                {motor?.errors.position ? "✅" : "❌"}
                            </DataTable.Cell>
                            <DataTable.Cell style={styles.cell}>
                                {motor?.errors.fault ? "✅" : "❌"}
                            </DataTable.Cell>
                            <DataTable.Cell style={styles.cell}>{motor?.values.position || 0}</DataTable.Cell>
                            <DataTable.Cell style={styles.cell}>{motor?.targets.position || 0}</DataTable.Cell>
                            <DataTable.Cell style={styles.cell}>{motor?.values.velocity || 0}</DataTable.Cell>
                            <DataTable.Cell style={styles.cell}>{motor?.values.torque || 0}</DataTable.Cell>
                            <DataTable.Cell style={styles.cell}>{motor?.values.temperature || 0}</DataTable.Cell>
                        </DataTable.Row>
                    );
                })}
            </ScrollView>
        </DataTable>
    )
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#aaaaaa',
    },
    scrollContainer: {
        flex: 1,
    },
    header: {
        borderBottomWidth: 3,
        borderBottomColor: '#888',
        height: 60
    },
    title: {
        width: 40,
        minHeight: 60,
        justifyContent: 'flex-start',
        alignItems: 'center',
        overflow: 'visible',
        transform: [{ rotate: '-90deg' }],
    },
    text: {
        color: 'black',
    },
    row: {
        minHeight: 25,
        borderBottomWidth: 1,
        borderBottomColor: '#888'
    },
    cell: {
        paddingVertical: 0,
        paddingHorizontal: 0,
    },
});