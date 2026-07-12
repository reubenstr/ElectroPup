import { useState } from "react";
import { View, Text, Pressable } from "react-native";
import { StyleSheet, useUnistyles } from "react-native-unistyles";
import { createText, createShadow } from "@/styles/themeComponents";
import { Status } from "@/services/data/dataTypes";

type IndicatorProps = {
  label: string;
  /* When present, renders on a second row below the label. */
  value?: string | number;
  /* Signal-colored fill (op status tiles). Takes precedence over `active`. */
  status?: Status;
  /* On/off fill for boolean state (foot contacts, motor enabled). */
  active?: boolean;
  /* Hover popup (web); used for the motor id -> joint name hint. */
  tooltip?: string;
  minWidth?: number;
};

function Indicator({
  label,
  value,
  status,
  active,
  tooltip,
  minWidth,
}: IndicatorProps) {
  const { theme } = useUnistyles();
  const [hovered, setHovered] = useState(false);

  const fill =
    status !== undefined
      ? statusFill(theme, status)
      : active !== undefined
        ? active
          ? theme.colors.indicator.on
          : theme.colors.indicator.off
        : theme.colors.indicator.off;

  const showTooltip = !!tooltip && hovered;

  return (
    <View style={styles.wrapper}>
      <Pressable
        onHoverIn={() => setHovered(true)}
        onHoverOut={() => setHovered(false)}
        style={[
          styles.container,
          { backgroundColor: fill },
          minWidth != null && { minWidth },
        ]}
      >
        <Text style={styles.label} numberOfLines={1}>
          {label}
        </Text>
        {value !== undefined && value !== "" && (
          <Text style={styles.value} numberOfLines={1}>
            {value}
          </Text>
        )}
      </Pressable>

      {showTooltip && (
        <View style={styles.tooltip} pointerEvents="none">
          <Text style={styles.tooltipText}>{tooltip}</Text>
        </View>
      )}
    </View>
  );
}

function statusFill(theme: { colors: { status: Record<string, string> } }, status: Status) {
  const map: Record<Status, string> = {
    [Status.None]: theme.colors.status.none,
    [Status.Standby]: theme.colors.status.standby,
    [Status.Active]: theme.colors.status.active,
    [Status.Warning]: theme.colors.status.warning,
    [Status.Critical]: theme.colors.status.critical,
    [Status.Error]: theme.colors.status.error,
  };
  return map[status] ?? theme.colors.status.none;
}

const styles = StyleSheet.create((theme) => ({
  wrapper: {
    position: "relative",
  },
  container: {
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: theme.padding.inset,
    paddingVertical: theme.padding.inset,
    borderWidth: theme.borderWidth.inset,
    borderColor: theme.colors.border.inset,
    borderRadius: theme.radius.inset,
    ...createShadow(theme, "small"),
  },
  label: {
    color: theme.colors.indicator.text,
    ...createText(theme, "secondary"),
    fontFamily: "OrbitronBold",
  },
  value: {
    color: theme.colors.indicator.text,
    ...createText(theme, "secondary"),
  },
  tooltip: {
    position: "absolute",
    bottom: "100%",
    left: 0,
    marginBottom: 4,
    paddingHorizontal: theme.padding.inset,
    paddingVertical: theme.padding.inset,
    backgroundColor: theme.colors.background.card,
    borderWidth: theme.borderWidth.card,
    borderColor: theme.colors.border.card,
    borderRadius: theme.radius.inset,
    zIndex: theme.zIndex.tooltip,
    maxWidth: 220,
    ...createShadow(theme, "medium"),
  },
  tooltipText: {
    color: theme.colors.text.primary,
    ...createText(theme, "secondary"),
  },
}));

export default Indicator;
