import React, { useRef, useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { AxisPad, AxisPadTouchEvent } from "@fustaro/react-native-axis-pad";
import { useDataTransfer } from '@/services/useDataTransfer';
import { ControlMessage, Command } from '@/interfaces/messages';
import Plot3D from '@/components/Plot3D';
import StatusIndicator from '@/components/indicators/StatusIndicator';
import ContactIndicator from '@/components/indicators/ContactIndicators';
import MotorIndicator from '@/components/indicators/MotorIndicator';
import MotorTooltip from '@/components/MotorTooltip';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useRouter } from 'expo-router';
import { Status } from '@/interfaces/messages';
import { motorNames } from '@/constants/motorNames';
import MotorTable from '@/components/MotorTable';

/*

    Joystick controller. Work in progress.

*/

export default function Viewer() {
    const router = useRouter();
    const { quadData: quadData, connected, sendMessage } = useDataTransfer();

    const leftX = useRef<number>(0);
    const leftY = useRef<number>(0);
    const rightX = useRef<number>(0);
    const rightY = useRef<number>(0);
    const command = useRef<Command>(Command.NO_UPDATE);

    const eStop = false; // TODO

    useEffect(() => {
        const intervalId = setInterval(() => {
            const message: ControlMessage = {
                leftX: leftX.current,
                leftY: leftY.current,
                rightX: rightX.current,
                rightY: rightY.current,
                command: command.current
            }
            sendMessage(JSON.stringify(message))

            command.current = Command.NO_UPDATE;
        }, 50);

        return () => clearInterval(intervalId);
    }, []);

    const goTo = (uri: string) => {
        router.push(uri as any)
    }

    const onTouchEventLeft = (event: AxisPadTouchEvent) => {
        if (["start", "end", "pan"].includes(event.eventType)) {
            leftX.current = -event.ratio.x;
            leftY.current = -event.ratio.y
        }
    };

    const onTouchEventRight = (event: AxisPadTouchEvent) => {
        if (["start", "end", "pan"].includes(event.eventType)) {
            leftX.current = -event.ratio.x;
            leftY.current = -event.ratio.y
        }
    };

    const setCommand = (newCommand: Command) => {
        command.current = newCommand;
    }

    // https://snack.expo.dev/@fustaro/fustaro-axis-pad-demo
    const padBackgroundColor = "#00000033";
    const padBorderColor = eStop ? "#AA0000" : "#009900";
    const knobColor = eStop ? "#550000aa" : "#005500aa";
    const AxisPadStyles = StyleSheet.create({
        pad: {
            backgroundColor: padBackgroundColor,
            borderColor: padBorderColor,
            borderWidth: 2,
        },
        knob: {
            backgroundColor: knobColor,
            borderColor: padBorderColor,
            borderWidth: 2,
        },
        stick: {
            width: 30,
            backgroundColor: padBackgroundColor,
            borderColor: padBorderColor,
            borderWidth: 2,
        },
    });

    const getMotor = (motorName: string) => {
        if (quadData?.motors && motorName in quadData?.motors) {
            return quadData.motors[motorName]
        }
    }

    return (
        <View style={styles.baseContainer}>
            <View style={TopNavStyles.topBar}>
                <View style={TopNavStyles.topBarColumn}>

                </View>
                <View style={TopNavStyles.topBarColumn}>
                    <Text style={TopNavStyles.topBarTitle}>ElectroPup</Text>
                </View>
                <View style={[TopNavStyles.topBarColumn, { justifyContent: 'flex-end' }]}>
                    <TouchableOpacity
                        style={TopNavStyles.topBarButton}
                        onPress={() => goTo('/data')}>
                        <Text style={TopNavStyles.topBarButtonText}>Data</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                        style={TopNavStyles.topBarButton}
                        onPress={() => goTo('/config')}>
                        <Text style={TopNavStyles.topBarButtonText}>Settings</Text>
                    </TouchableOpacity>
                </View>
            </View>

            <View style={styles.baseColumnContainer}>
                <View style={styles.baseColumnControls}>
                    <View style={styles.controlContainer}>
                        <View style={styles.controlRowTop}>

                            <View style={{ flexDirection: 'row', justifyContent: 'space-between', gap: 10 }}>
                                <TouchableOpacity
                                    style={[ButtonStyles.iconButton, ButtonStyles.primary]}
                                    onPress={() => setCommand(Command.GAMEPAD_INPUT)}>
                                    <Icon name='gamepad-square' size={24} color='white' />
                                </TouchableOpacity>
                                <TouchableOpacity
                                    style={[ButtonStyles.iconButton, ButtonStyles.primary]}
                                    onPress={() => setCommand(Command.TOUCH_INPUT)}>
                                    <Icon name='tablet' size={24} color='white' />
                                </TouchableOpacity>
                            </View>

                            <TouchableOpacity
                                style={[ButtonStyles.button, ButtonStyles.primary]}
                                onPress={() => setCommand(Command.STAND)}>
                                <Text style={ButtonStyles.text}>STAND</Text>
                            </TouchableOpacity>
                        </View>
                        <View style={styles.controlRowCenterLeft}>
                            <AxisPad
                                id={`pad-left-${Math.floor(Math.random() * 1000) + 1}`}
                                size={140}
                                controlSize={60}
                                disableY={false}
                                padBackgroundStyle={AxisPadStyles.pad}
                                controlStyle={AxisPadStyles.knob}
                                stickStyle={AxisPadStyles.stick}
                                ignoreTouchDownInPadArea={false}
                                initialTouchType={"no-snap"}
                                onTouchEvent={onTouchEventLeft}
                            />
                        </View>
                        <View style={styles.controlRowBottom}>
                            <TouchableOpacity
                                style={[ButtonStyles.button, ButtonStyles.primary]}
                                onPress={() => setCommand(Command.SIT)}>
                                <Text style={ButtonStyles.text}>SIT</Text>
                            </TouchableOpacity>
                        </View>
                    </View>

                </View>
                <View style={styles.baseColumnCenter}>
                    <Text> Add Indicators</Text>
                </View>
                <View style={styles.baseColumnControls}>
                    <View style={styles.controlContainer}>
                        <View style={styles.controlRowTop}>
                            <TouchableOpacity
                                style={[ButtonStyles.button, ButtonStyles.primary]}
                                onPress={() => setCommand(Command.POSE)}>
                                <Text style={ButtonStyles.text}>POSE</Text>
                            </TouchableOpacity>
                        </View>
                        <View style={styles.controlRowCenterRight}>
                            <AxisPad
                                id={`pad-right-${Math.floor(Math.random() * 1000) + 1}`}
                                size={140}
                                controlSize={60}
                                disableY={false}
                                padBackgroundStyle={AxisPadStyles.pad}
                                controlStyle={AxisPadStyles.knob}
                                stickStyle={AxisPadStyles.stick}
                                ignoreTouchDownInPadArea={false}
                                initialTouchType={"no-snap"}
                                onTouchEvent={onTouchEventRight}
                            />
                        </View>
                        <View style={styles.controlRowBottom}>
                            <TouchableOpacity
                                style={[ButtonStyles.button, ButtonStyles.primary]}
                                onPress={() => setCommand(Command.BIAS_WALK)}>
                                <Text style={ButtonStyles.text}>B. WALK</Text>
                            </TouchableOpacity>
                            <TouchableOpacity
                                style={[ButtonStyles.button, ButtonStyles.primary]}
                                onPress={() => setCommand(Command.VECTOR_WALK)}>
                                <Text style={ButtonStyles.text}>V. WALK</Text>
                            </TouchableOpacity>
                        </View>
                    </View>
                </View>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    baseContainer: {
        flexDirection: 'column',
        flex: 1,
        width: '100%',
    },
    baseColumnContainer: {
        flexDirection: 'row',
        flex: 1,
        width: '100%',
    },
    baseColumnControls: {
        justifyContent: 'center',
        alignItems: 'center',
        padding: 10,
    },
    baseColumnCenter: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 10,
    },

    controlContainer: {
        flexDirection: 'column',
        flex: 1,
    },
    controlRowTop: {
        flex: 1,
        justifyContent: 'flex-end',
        alignItems: 'center',
    },
    controlRowCenterLeft: {
        marginVertical: 20,
        paddingLeft: 10,
        justifyContent: 'center',
        alignItems: 'center',
    },
    controlRowCenterRight: {
        marginVertical: 20,
        paddingRight: 10,
        justifyContent: 'center',
        alignItems: 'center',
    },
    controlRowBottom: {
        flex: 1,
        justifyContent: 'flex-start',
        alignItems: 'center',
    },

    centerColumnIndicatorRow: {
        flexDirection: 'row',
        width: '100%',
        justifyContent: 'center',
    },
    centerColumnPlotRow: {
        flex: 1,
        flexDirection: 'row',
        width: '100%',
        backgroundColor: "#2a2a2a"
    },
    plotContainer: {
        flex: 1,
        alignContent: 'center',
        justifyContent: 'center',
    },
    motorTableContainer: {
        flex: 1 / 2,
        marginTop: 10,
        marginRight: 10,
        marginBottom: 10,
    },

    verticalLine: {
        width: 2,
        backgroundColor: '#000',
        marginHorizontal: 5,
        marginVertical: 5
    },
});

const TopNavStyles = StyleSheet.create({
    topBar: {
        height: 50,
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottomWidth: 1,
        borderBottomColor: '#000',
        paddingHorizontal: 10,
    },
    topBarTitle: {
        flex: 1,
        textAlign: 'center',
        fontSize: 24,
        fontWeight: 'bold',
        color: '#4caf50',
    },
    topBarColumn: {
        flex: 1,
        flexDirection: 'row',
        alignItems: 'center',
    },
    topBarButton: {
        marginLeft: 10,
        backgroundColor: "#666",
        paddingVertical: 4,
        paddingHorizontal: 8,
        borderRadius: 5,

    },
    topBarButtonText: {
        fontSize: 18,
        fontWeight: 'bold',
        color: '#fff',
    },
})

const ButtonStyles = StyleSheet.create({
    button: {
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
        paddingVertical: 8,
        paddingHorizontal: 20,
        borderRadius: 5,
        margin: 3,
        width: 125,
        backgroundColor: '#3344ff',
    },
    iconButton: {
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
        paddingVertical: 0,
        paddingHorizontal: 0,
        borderRadius: 5,
        margin: 3,
        width: 50,
        height: 32,
        backgroundColor: '#3344ff',
    },
    text: {
        fontWeight: 'bold',
        color: '#fff',
    },
    primary: {
        backgroundColor: '#3344ff',
    },
    showMotorInfoButton: {
        flexDirection: 'row',
        justifyContent: 'center',
        alignItems: 'center',
        paddingVertical: 8,
        paddingHorizontal: 20,
        borderRadius: 5,
        margin: 3,
        width: 180,
        backgroundColor: '#3344ff',
    },
});
