import { View, Pressable, Text } from "react-native";
import { StyleSheet, useUnistyles } from "react-native-unistyles";
import { createText, createShadow } from "@/styles/themeComponents";
import MaterialCommunityIcons from "@expo/vector-icons/MaterialCommunityIcons";

const PRESSED_OPACITY = 0.6;
const DEFAULT_OPACITY = 1.0;

type IconName =
  "add" | "delete" | "save" | "edit" | "close" | "check" | "info" | "sensor";

const iconMap: Record<IconName, keyof typeof MaterialCommunityIcons.glyphMap> =
  {
    add: "plus",
    delete: "delete",
    save: "content-save",
    edit: "pencil",
    close: "close",
    check: "check",
    info: "information",
    sensor: "monitor",
  };

type ButtonType =
  "action" | "info" | "success" | "warning" | "danger" | "navigation";

type BaseButtonProps = {
  onPress: () => void;
  buttonType?: ButtonType;
  isSelected?: boolean;
  size?: number;
  disabled?: boolean;
  numberOfLines?: number;
};

type ButtonProps = BaseButtonProps &
  (
    | { label: string; iconName?: IconName }
    | { label?: string; iconName: IconName }
  );

const Button = ({
  label,
  iconName,
  onPress,
  buttonType = "action",
  isSelected = false,
  size,
  disabled = false,
  numberOfLines,
}: ButtonProps) => {
  const { theme } = useUnistyles();

  const actualIconName = iconName ? iconMap[iconName] : undefined;
  const hasIconOnly = !!iconName && !label;
  const hasBoth = !!iconName && !!label;

  const variantColor = theme.colors.button.variants[buttonType];

  const backgroundColor = disabled
    ? theme.colors.button.disabled.background
    : isSelected
      ? theme.colors.button.active
      : theme.colors.button.background;

  const borderColor = disabled
    ? theme.colors.button.disabled.border
    : variantColor;

  const textColor = disabled
    ? theme.colors.button.disabled.text
    : isSelected
      ? theme.colors.text.inverse
      : theme.colors.button.text;

  const iconColor = textColor;

  const iconSize = size ? size : theme.size.control.icon;

  return (
    <Pressable
      onPress={onPress}
      disabled={disabled}
      style={({ pressed }) => [
        defaultStyles.button,
        hasIconOnly && defaultStyles.iconOnlyButton,
        {
          backgroundColor,
          borderColor,
          opacity: pressed ? PRESSED_OPACITY : DEFAULT_OPACITY,
        },
      ]}
    >
      {hasBoth ? (
        <View style={defaultStyles.iconTextContainer}>
          <MaterialCommunityIcons
            name={actualIconName!}
            size={iconSize}
            color={iconColor}
          />
          <Text
            style={[defaultStyles.buttonText, { color: textColor }]}
            numberOfLines={numberOfLines}
          >
            {label}
          </Text>
        </View>
      ) : hasIconOnly ? (
        <MaterialCommunityIcons
          name={actualIconName!}
          size={iconSize}
          color={iconColor}
        />
      ) : (
        <Text
          style={[defaultStyles.buttonText, { color: textColor }]}
          numberOfLines={numberOfLines}
        >
          {label}
        </Text>
      )}
    </Pressable>
  );
};

const defaultStyles = StyleSheet.create((theme) => ({
  button: {
    paddingHorizontal: theme.padding.control.horizontal,
    paddingVertical: theme.padding.control.vertical,
    borderRadius: theme.radius.control,
    borderWidth: theme.borderWidth.control,
    borderColor: theme.colors.button.border,
    ...createShadow(theme, "small"),
  },
  iconOnlyButton: {
    paddingHorizontal: theme.padding.control.vertical,
    paddingVertical: theme.padding.control.vertical,
  },
  iconTextContainer: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  buttonText: {
    ...createText(theme, "control"),
  },
}));

export default Button;
