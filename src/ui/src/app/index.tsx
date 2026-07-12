import { useState } from "react";
import { View, Text } from "react-native";
import { StyleSheet } from "react-native-unistyles";
import { createText, createContainer } from "@/styles/themeComponents";
import Plot3D from "@/components/viewer/Plot3D";
import Indicator from "@/components/viewer/Indicator";
import MotorTable from "@/components/viewer/MotorTable";
import Button from "@/components/primatives/Button";
import { useDataStore, ConnectionStatus } from "@/services/data/useDataStore";
import { Status } from "@/services/data/dataTypes";
import { motorNames, MotorKey } from "@/services/data/motorNames";

const CONNECTION_STATUS: Record<ConnectionStatus, Status> = {
  connected: Status.Active,
  connecting: Status.Warning,
  disconnected: Status.Error,
};

const motorKeys = Object.keys(motorNames) as MotorKey[];
const leftMotorKeys = motorKeys.slice(0, motorKeys.length / 2);
const rightMotorKeys = motorKeys.slice(motorKeys.length / 2);

const fixed = (value: number | string | undefined, digits = 2) => {
  const n = Number(value);
  return Number.isNaN(n) ? "N/A" : n.toFixed(digits);
};

export default function PlotScreen() {
  const data = useDataStore((s) => s.data);
  const status = useDataStore((s) => s.status);
  const [showMotorInfo, setShowMotorInfo] = useState(false);

  const sys = data?.status;
  const ik = data?.ikParameters;
  const motion = data?.motionParameters;

  return (
    <View style={styles.screen}>
      {/* Operational state */}
      <View style={styles.indicatorRow}>
        <Indicator label="Robot" value={status} status={CONNECTION_STATUS[status]} minWidth={110} />
        <View style={styles.divider} />
        <Indicator label="OpMode" value={sys?.opMode?.state} minWidth={100} />
        <Indicator label="Target" value={sys?.targetMotion?.state} minWidth={100} />
        <Indicator
          label="Motion"
          value={sys?.motion?.state}
          status={sys?.motion?.state === "standby" ? Status.Standby : undefined}
          minWidth={100}
        />
        <Indicator label="Gait" value={sys?.gait?.state} minWidth={100} />
        <Indicator label="Input" value={sys?.input?.state} minWidth={100} />
      </View>

      {/* Subsystem health */}
      <View style={styles.indicatorRow}>
        <Indicator label="MOT" status={sys?.motor?.status} />
        <View style={styles.divider} />
        <Indicator label="IK" status={sys?.ik?.status} />
        <Indicator label="JA" status={sys?.jointAngle?.status} />
        <View style={styles.divider} />
        <Indicator label="GPIO" status={sys?.gpio?.status} />
        <Indicator label="I2C" status={sys?.smbus?.status} />
        <Indicator label="IMU" status={sys?.imu?.status} />
        <Indicator label="CAN0" status={sys?.can0?.status} />
        <Indicator label="CAN1" status={sys?.can1?.status} />
        <View style={styles.divider} />
        <Indicator label="JOY" value={sys?.gamepad?.battery} status={sys?.gamepad?.status} />
        <Indicator label="Voltage" value={fixed(sys?.voltage?.voltage)} status={sys?.voltage?.status} />
      </View>

      {/* Plot + motor overlays */}
      <View style={styles.plotRow}>
        <View style={styles.plotContainer}>
          <Plot3D data={data} />

          {/*
          <View style={styles.leftContacts}>
            <Indicator label="LF" active={!!data?.contacts?.leftFront} />
            <Indicator label="LB" active={!!data?.contacts?.leftBack} />
          </View>
          <View style={styles.rightContacts}>
            <Indicator label="RF" active={!!data?.contacts?.rightFront} />
            <Indicator label="RB" active={!!data?.contacts?.rightBack} />
          </View>
          */}

          <View style={styles.leftMotors}>
            {leftMotorKeys.map((key) => (
              <Indicator
                key={key}
                label={key}
                active={!!data?.motors?.[key]?.enabled}
                tooltip={motorNames[key]}
              />
            ))}
          </View>
          <View style={styles.rightMotors}>
            {rightMotorKeys.map((key) => (
              <Indicator
                key={key}
                label={key}
                active={!!data?.motors?.[key]?.enabled}
                tooltip={motorNames[key]}
              />
            ))}
          </View>

          <View style={styles.motorInfoButton}>
            <Button
              label={showMotorInfo ? "Hide Motor Info" : "Show Motor Info"}
              buttonType="action"
              onPress={() => setShowMotorInfo((v) => !v)}
            />
          </View>
        </View>

        {showMotorInfo && (
          <View style={styles.motorTable}>
            <MotorTable motors={data?.motors} />
          </View>
        )}
      </View>

      {/* Telemetry panels */}
      <View style={styles.infoRow}>
        <InfoPanel title="Loop Times">
          <InfoText>Main: {fixed(sys?.loopTimes?.main)} ms</InfoText>
          <InfoText>Motion: {fixed(sys?.loopTimes?.motion)} ms</InfoText>
          <InfoText>CAN 0: {fixed(sys?.loopTimes?.can0)} ms</InfoText>
          <InfoText>CAN 1: {fixed(sys?.loopTimes?.can1)} ms</InfoText>
        </InfoPanel>

        <InfoPanel title="IK Inputs">
          <View style={styles.infoColumns}>
            <View style={styles.infoColumn}>
              <InfoLabel>Translation</InfoLabel>
              <InfoText>Forward: {fixed(ik?.forwardTranslation, 3)}</InfoText>
              <InfoText>Side: {fixed(ik?.sideTranslation, 3)}</InfoText>
              <InfoText>Height: {fixed(ik?.heightTranslation, 3)}</InfoText>
            </View>
            <View style={styles.infoColumn}>
              <InfoLabel>Rotation</InfoLabel>
              <InfoText>Roll: {fixed(ik?.roll)}</InfoText>
              <InfoText>Pitch: {fixed(ik?.pitch)}</InfoText>
              <InfoText>Yaw: {fixed(ik?.yaw)}</InfoText>
            </View>
          </View>
        </InfoPanel>

        <InfoPanel title="Motion Inputs">
          <InfoLabel>Velocities</InfoLabel>
          <InfoText>Forward: {fixed(motion?.forwardVelocity, 3)}</InfoText>
          <InfoText>Lateral: {fixed(motion?.lateralVelocity, 3)}</InfoText>
          <InfoText>Angular: {fixed(motion?.angularVelocity, 3)}</InfoText>
        </InfoPanel>

        <InfoPanel title="IMU">
          <InfoText>Roll: {fixed(sys?.imu?.roll)}°</InfoText>
          <InfoText>Pitch: {fixed(sys?.imu?.pitch)}°</InfoText>
        </InfoPanel>
      </View>
    </View>
  );
}

function InfoPanel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <View style={styles.infoPanel}>
      <Text style={styles.infoHeader}>{title}</Text>
      <View style={styles.infoLine} />
      {children}
    </View>
  );
}

function InfoLabel({ children }: { children: React.ReactNode }) {
  return <Text style={styles.infoLabel}>{children}</Text>;
}

function InfoText({ children }: { children: React.ReactNode }) {
  return <Text style={styles.infoText}>{children}</Text>;
}

const styles = StyleSheet.create((theme) => ({
  screen: {
    flex: 1,
    gap: theme.gap.surface,
  },
  indicatorRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    alignItems: "center",
    justifyContent: "center",
    gap: theme.gap.control,
  },
  divider: {
    alignSelf: "stretch",
    width: theme.borderWidth.divider,
    backgroundColor: theme.colors.divider,
  },
  plotRow: {
    flex: 1,
    flexDirection: "row",
    ...createContainer(theme, "inset"),
    gap: theme.gap.surface,
  },
  plotContainer: {
    flex: 1,
  },
  motorTable: {
    flex: 0.8,
  },
  leftContacts: {
    position: "absolute",
    left: 56,
    height: "50%",
    justifyContent: "center",
    gap: theme.gap.inset,
  },
  rightContacts: {
    position: "absolute",
    right: 56,
    height: "50%",
    justifyContent: "center",
    gap: theme.gap.inset,
  },
  leftMotors: {
    position: "absolute",
    left: 0,
    top: 0,
    bottom: 0,
    justifyContent: "center",
    gap: theme.gap.inset,
  },
  rightMotors: {
    position: "absolute",
    right: 0,
    top: 0,
    bottom: 0,
    justifyContent: "center",
    gap: theme.gap.inset,
  },
  motorInfoButton: {
    position: "absolute",
    right: theme.padding.inset,
    bottom: theme.padding.inset,
  },
  infoRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: theme.gap.surface,
  },
  infoPanel: {
    ...createContainer(theme, "card"),
    flexGrow: 1,
    flexBasis: 200,
  },
  infoHeader: {
    color: theme.colors.text.primary,
    ...createText(theme, "header2"),
  },
  infoLine: {
    height: theme.borderWidth.divider,
    backgroundColor: theme.colors.divider,
    marginVertical: theme.gap.inset,
  },
  infoColumns: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: theme.gap.card,
  },
  infoColumn: {
    flexGrow: 1,
    minWidth: 110,
    gap: 2,
  },
  infoLabel: {
    color: theme.colors.text.secondary,
    ...createText(theme, "secondary"),
    fontFamily: "OrbitronBold",
  },
  infoText: {
    color: theme.colors.text.primary,
    ...createText(theme, "mono"),
  },
}));
