import React, { useRef, useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from 'react-native';
import { useDataTransfer } from '@/services/useDataTransfer';
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

export default function Viewer() {
    const router = useRouter();
    const { quadData: quadData, connected, sendMessage } = useDataTransfer();

    const [showMotorInfo, setShowMotorInfo] = useState(false);

    const goTo = (uri: string) => {
        router.push(uri as any)
    }

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
                <View style={styles.baseColumnCenter}>
                    <View style={styles.indicatorRow}>
                        <StatusIndicator
                            name='Quadruped'
                            value={connected ? "connected" : "disconnected"}
                            status={connected ? Status.Active : Status.Error}
                            style={{ width: 100 }}
                        />
                        <View style={styles.verticalLine} />
                        <StatusIndicator
                            name='OpMode'
                            value={quadData?.status?.opMode?.state}
                            style={{ width: 100 }}
                        />
                        <StatusIndicator
                            name='Target'
                            value={quadData?.status?.targetMotion?.state}
                            style={{ width: 100 }}
                        />
                        <StatusIndicator
                            name='Motion'
                            value={quadData?.status?.motion?.state}
                            style={{
                                width: 100,
                                backgroundColor:
                                    quadData?.status?.motion?.state === 'standby'
                                        ? '#ff9800'
                                        : undefined,
                            }}
                        />
                        <StatusIndicator
                            name='Gait'
                            value={quadData?.status?.gait?.state}
                            style={{ width: 100 }}
                        />
                        <StatusIndicator
                            name='Input'
                            value={quadData?.status?.input?.state}
                            style={{ width: 100 }}
                        />
                    </View>

                      <View style={styles.horizontalLine} />

                    <View style={styles.indicatorRow}>
                         <StatusIndicator
                            name='MOT'
                            status={quadData?.status?.motor?.status}
                        />
                        <View style={styles.verticalLine} />
                        <StatusIndicator
                            name='IK'
                            status={quadData?.status?.ik?.status}
                        />
                        <StatusIndicator
                            name='JA'
                            status={quadData?.status?.jointAngle?.status}
                        />
                        <View style={styles.verticalLine} />
                        <StatusIndicator
                            name='GPIO'
                            status={quadData?.status?.gpio?.status}
                        />
                        <StatusIndicator
                            name='I2C'
                            status={quadData?.status?.smbus?.status}
                        />                        
                        <StatusIndicator
                            name='IMU'
                            status={quadData?.status?.imu?.status}
                        />
                        <StatusIndicator
                            name='CAN0'
                            status={quadData?.status?.can0?.status}
                        />
                        <StatusIndicator
                            name='CAN1'
                            status={quadData?.status?.can1?.status}
                        />
                        <View style={styles.verticalLine} />
                        <StatusIndicator
                            name='JOY'
                            value={quadData?.status?.gamepad?.battery}
                            status={quadData?.status?.gamepad?.status}
                        />
                        <StatusIndicator
                            name='Voltage'
                            value={quadData?.status?.voltage?.voltage}
                            status={quadData?.status?.voltage?.status}
                        />                       
                    </View>

                    <View style={styles.plotRow}>
                        <View style={styles.plotContainer}>
                            <Plot3D quadData={quadData} />

                            <View style={OverlayStyles.leftContacts}>
                                <ContactIndicator
                                    name='LF'
                                    state={quadData?.contacts?.leftFront}
                                />
                                <ContactIndicator
                                    name='LB'
                                    state={quadData?.contacts?.leftBack}
                                />
                            </View>

                            <View style={OverlayStyles.rightContacts}>
                                <ContactIndicator
                                    name='RF'
                                    state={quadData?.contacts?.rightFront}
                                />
                                <ContactIndicator
                                    name='RB'
                                    state={quadData?.contacts?.rightBack}
                                />
                            </View>

                            <View style={OverlayStyles.leftMotors}>
                                {Object.entries(motorNames)
                                    .slice(0, Math.ceil(Object.keys(motorNames).length / 2))
                                    .map(([key, value]) => (
                                        <MotorTooltip key={key} label={key} value={value}>
                                            <MotorIndicator name={key} state={getMotor(key)?.enabled || false} />
                                        </MotorTooltip>
                                    ))}
                            </View>

                            <View style={OverlayStyles.rightMotors}>
                                {Object.entries(motorNames)
                                    .slice(Math.ceil(Object.keys(motorNames).length / 2))
                                    .map(([key, value]) => (
                                        <MotorIndicator name={key} state={getMotor(key)?.enabled || false} />
                                    ))}
                            </View>

                           

                            
                        </View>
                        {
                            showMotorInfo &&
                            <View style={styles.motorTableContainer}>
                                <MotorTable />
                            </View>
                        }
                        <View style={OverlayStyles.showMotorInfoButton}>
                            <TouchableOpacity
                                style={ButtonStyles.showMotorInfoButton}
                                onPress={() => setShowMotorInfo(!showMotorInfo)}>
                                <Text style={ButtonStyles.text}>{showMotorInfo ? 'HIDE MOTOR INFO' : 'SHOW MOTOR INFO'}</Text>
                            </TouchableOpacity>
                        </View>
                    </View>

                     <View style={styles.bottomInfoRow}>

                        <View style={OverlayStyles.infoContainer}>
                                <Text style={OverlayStyles.header}>Loop Times</Text>
                                <View style={OverlayStyles.line} />
                                <View style={OverlayStyles.columns}>
                                    <View style={OverlayStyles.column}>
                                        <Text>Main: {quadData?.status?.loopTimes.main.toFixed(2)} ms</Text>
                                        <Text>Motion: {quadData?.status?.loopTimes.motion.toFixed(2)} ms</Text>
                                        <Text>CAN 0: {quadData?.status?.loopTimes.can0.toFixed(2)} ms</Text>
                                        <Text>CAN 1: {quadData?.status?.loopTimes.can1.toFixed(2)} ms</Text>
                                    </View>
                                </View>
                            </View>

                            <View style={OverlayStyles.infoContainer}>
                                <Text style={OverlayStyles.header}>IK Inputs</Text>
                                <View style={OverlayStyles.line} />
                                <View style={OverlayStyles.columns}>
                                    <View style={OverlayStyles.column}>
                                        <Text style={OverlayStyles.text}>Translation</Text>
                                        <Text>Forward: {quadData?.ikParameters?.forwardTranslation?.toFixed(3)}</Text>
                                        <Text>Side: {quadData?.ikParameters?.sideTranslation?.toFixed(3)}</Text>
                                        <Text>Height: {quadData?.ikParameters?.heightTranslation?.toFixed(3)}</Text>
                                    </View>
                                    <View style={OverlayStyles.column}>
                                        <Text style={OverlayStyles.text}>Rotation</Text>
                                        <Text>Roll: {quadData?.ikParameters?.roll?.toFixed(2)}</Text>
                                        <Text>Pitch: {quadData?.ikParameters?.pitch?.toFixed(2)}</Text>
                                        <Text>Yaw: {quadData?.ikParameters?.yaw?.toFixed(2)}</Text>
                                    </View>
                                </View>
                                <Text style={OverlayStyles.mHeader}>Motion Inputs</Text>
                                <View style={OverlayStyles.line} />
                                <View style={OverlayStyles.columns}>
                                    <View style={OverlayStyles.column}>
                                        <Text style={OverlayStyles.text}>Velocities</Text>
                                        <Text>Forward: {quadData?.motionParameters?.forwardVelocity?.toFixed(3)}</Text>
                                        <Text>Lateral: {quadData?.motionParameters?.lateralVelocity?.toFixed(3)}</Text>
                                        <Text>Angular: {quadData?.motionParameters?.angularVelocity?.toFixed(3)}</Text>
                                    </View>
                                    <View style={OverlayStyles.column}>
                                       
                                    </View>
                                </View>
                            </View>

                         <View style={OverlayStyles.infoContainer}>
                                <Text style={OverlayStyles.header}>IMU</Text>
                                <View style={OverlayStyles.line} />
                                <View style={OverlayStyles.columns}>
                                    <View style={OverlayStyles.column}>
                                        <Text>
                                            Roll: {isNaN(Number(quadData?.status?.imu?.roll)) ? 'N/A' : Number(quadData?.status?.imu?.roll).toFixed(2)}°
                                        </Text>
                                        <Text>
                                            Pitch: {isNaN(Number(quadData?.status?.imu?.pitch)) ? 'N/A' : Number(quadData?.status?.imu?.pitch).toFixed(2)}°
                                        </Text>
                                    </View>
                                </View>
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
    baseColumnCenter: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
        padding: 10,
    },
    controlRowBottom: {
        flex: 1,
        justifyContent: 'flex-start',
        alignItems: 'center',
    },
    indicatorRow: {
        flexDirection: 'row',
        width: '100%',
        justifyContent: 'center',
    },
    plotRow: {
        flex: 1,
        flexDirection: 'row',
        width: '100%',
        backgroundColor: "#2a2a2a"
    },
     bottomInfoRow: {      
        marginTop: 5, 
       flexDirection: 'row',
        width: '100%',
        justifyContent: 'center',
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
        width: 1,
        backgroundColor: '#000',
        marginHorizontal: 5,
        marginVertical: 5
    },
     horizontalLine: {
        width: '100%',
        height: 1,
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


const OverlayStyles = StyleSheet.create({
    leftContacts: {
        position: 'absolute',
        left: 60,
        justifyContent: 'center',
        height: '50%',
    },

    rightContacts: {
        position: 'absolute',
        right: 60,
        justifyContent: 'center',
        height: '50%',
    },

    leftMotors: {
        position: 'absolute',
        left: 5,
        justifyContent: 'center',
        height: '90%',
    },

    rightMotors: {
        position: 'absolute',
        right: 5,
        justifyContent: 'center',
        height: '90%',
    },

    infoContainer: {
        padding: 5,
        margin: 5,
        borderRadius: 4,
        backgroundColor: '#aaa',
    },
    header: {
        fontWeight: 'bold',
        fontSize: 16,
        marginBottom: 4,
    },
    line: {
        height: 1,
        backgroundColor: '#000',
        marginBottom: 8,
    },
    text: {
        fontWeight: '600',
        marginBottom: 4,
    },
    columns: {
        flexDirection: 'row',
        justifyContent: 'space-between',
    },
    column: {
        marginRight: 15,
    },
    mHeader: {
        fontWeight: 'bold',
        fontSize: 16,
        marginTop: 14,
        marginBottom: 4,

    },
    showMotorInfoButton: {
        position: 'absolute',
        right: 5,
        bottom: 5
    }
});


