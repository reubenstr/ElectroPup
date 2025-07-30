import React, { useRef, useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { motorNames } from '@/constants/motorNames';
import { useDataTransfer } from '@/services/useDataTransfer';
import { VerticalText } from './verticalText';

const columnWidths = [40, 30, 30, 30, 30, 50, 50, 50, 50];
const headerTitles = ['Motor', 'Enabled', 'AllowComms', 'AllowMotion', 'CommsError', 'Position', 'Speed', 'Temperature', 'Watts']

export default function MotorTable() {

    const { quadData } = useDataTransfer();

    if (!quadData) {
        return (
            <Text style={styles.loadingText}>No Data</Text>
        )
    }

    const getMotor = (motorName: string) => {
        if (quadData?.motors && motorName in quadData?.motors) {
            return quadData.motors[motorName]
        }
    }

    const getValue = (value: number | undefined) => {
        if (value != undefined)
            return Math.round(value) 
        return '-';
    }

    return (
        <View style={styles.table}>
            <View style={styles.headerRow}>
                {headerTitles.map((title, index) => (
                    <View key={index} style={[styles.cell, { width: columnWidths[index] }]}>
                        <VerticalText text={title} />
                    </View>
                ))}
            </View>

            <ScrollView style={styles.scrollContainer}>
                {Object.entries(motorNames).map(([key, value]) => {
                    const motor = getMotor(key);
                    const rowData = [
                        key,
                        motor?.enabled === undefined ? "-" : motor.enabled ? "✅" : "❌",
                        motor?.allowComms === undefined ? "-" : motor.allowComms ? "✅" : "❌",
                        motor?.allowMotion === undefined ? "-" : motor.allowMotion ? "✅" : "❌",
                        motor?.commsError === undefined ? "-" : motor.commsError ? "❌" : "-",
                        getValue(motor?.values?.positionDegrees),
                        getValue(motor?.values?.motorSpeed),
                        getValue(motor?.values?.temperature),
                        getValue(motor?.values?.watts)
                    ];

                    return (
                        <View key={key} style={styles.dataRow}>
                            {rowData.map((cellData, index) => (
                                <View key={index} style={[styles.cell, { width: columnWidths[index] }]}>
                                    <Text style={styles.cellText}>{cellData}</Text>
                                </View>
                            ))}
                        </View>
                    );
                })}
            </ScrollView>
        </View>
    )
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#aaaaaa',
    },
    loadingText: {
        fontSize: 18,
        color: 'white',
    },
    table: {
        flex: 1,
        backgroundColor: '#aaa',
    },
    headerRow: {
        flexDirection: 'row',
        borderBottomWidth: 2,
        borderBottomColor: '#888',
        paddingBottom: 4,
    },
    headerCell: {
        justifyContent: 'center',
        alignItems: 'center',
        borderRightWidth: 1,
        borderColor: '#555',
        height: 100, // matches rotated text height
        overflow: 'visible',
    },
    dataRow: {
        flexDirection: 'row',
        borderBottomWidth: 1,
        borderBottomColor: '#555',
        minHeight: 30,
    },
    cell: {
        justifyContent: 'center',
        alignItems: 'center',
        borderRightWidth: 1,
        borderColor: '#555',
        paddingVertical: 4,
    },
    cellText: {
        fontSize: 12,
        color: 'black',
        textAlign: 'center',
    },
    scrollContainer: {
        flexGrow: 1,
    }
});