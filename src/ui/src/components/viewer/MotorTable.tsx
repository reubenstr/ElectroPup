import { View, Text, ScrollView } from "react-native";
import { StyleSheet } from "react-native-unistyles";
import { createText, createContainer } from "@/styles/themeComponents";
import { motorNames } from "@/services/data/motorNames";
import { MotorState } from "@/services/data/dataTypes";

type Column = {
  key: string;
  header: string;
  flex: number;
  render: (motor: MotorState | undefined) => string;
};

const bool = (v: boolean | undefined, on = "✓", off = "✕") =>
  v === undefined ? "–" : v ? on : off;

const num = (v: number | undefined) => (v === undefined ? "–" : String(Math.round(v)));

const COLUMNS: Column[] = [
  { key: "name", header: "Motor", flex: 1.4, render: () => "" },
  { key: "enabled", header: "En", flex: 1, render: (m) => bool(m?.enabled) },
  { key: "comms", header: "Comm", flex: 1, render: (m) => bool(m?.allowComms) },
  { key: "motion", header: "Motn", flex: 1, render: (m) => bool(m?.allowMotion) },
  { key: "error", header: "Err", flex: 1, render: (m) => bool(m?.commsError, "✕", "–") },
  { key: "pos", header: "Pos", flex: 1.2, render: (m) => num(m?.values?.positionDegrees) },
  { key: "speed", header: "Spd", flex: 1.2, render: (m) => num(m?.values?.motorSpeed) },
  { key: "temp", header: "Temp", flex: 1.2, render: (m) => num(m?.values?.temperature) },
  { key: "current", header: "Cur", flex: 1.2, render: (m) => num(m?.values?.current) },
];

interface MotorTableProps {
  motors?: Record<string, MotorState>;
}

export default function MotorTable({ motors }: MotorTableProps) {
  return (
    <View style={styles.table}>
      <View style={styles.headerRow}>
        {COLUMNS.map((col) => (
          <Text
            key={col.key}
            style={[styles.headerCell, { flex: col.flex }]}
            numberOfLines={1}
          >
            {col.header}
          </Text>
        ))}
      </View>

      <ScrollView>
        {Object.keys(motorNames).map((motorKey) => {
          const motor = motors?.[motorKey];
          return (
            <View key={motorKey} style={styles.row}>
              {COLUMNS.map((col) => (
                <Text
                  key={col.key}
                  style={[styles.cell, { flex: col.flex }]}
                  numberOfLines={1}
                >
                  {col.key === "name" ? motorKey : col.render(motor)}
                </Text>
              ))}
            </View>
          );
        })}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create((theme) => ({
  table: {
    flex: 1,
    ...createContainer(theme, "card"),
    padding: 0,
    overflow: "hidden",
  },
  headerRow: {
    flexDirection: "row",
    backgroundColor: theme.colors.background.inset,
    borderBottomWidth: theme.borderWidth.divider,
    borderBottomColor: theme.colors.divider,
    paddingVertical: theme.padding.inset,
    paddingHorizontal: theme.padding.inset,
  },
  headerCell: {
    color: theme.colors.text.primary,
    textAlign: "center",
    ...createText(theme, "secondary"),
    fontFamily: "OrbitronBold",
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    borderBottomWidth: theme.borderWidth.divider,
    borderBottomColor: theme.colors.divider,
    paddingVertical: theme.padding.inset,
    paddingHorizontal: theme.padding.inset,
  },
  cell: {
    color: theme.colors.text.primary,
    textAlign: "center",
    ...createText(theme, "mono"),
  },
}));
