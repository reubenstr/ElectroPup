import { Children, cloneElement, isValidElement } from "react";
import {
  View,
  StyleProp,
  ViewStyle,
  Platform,
  StyleSheet as RNStyleSheet,
} from "react-native";
import { StyleSheet, useUnistyles } from "react-native-unistyles";
import {
  Picker as RNPicker,
  PickerProps,
  PickerItemProps,
} from "@react-native-picker/picker";

/*
  This is a wrapper around @react-native-picker/picker for applying custom styles.
*/

type ItemValue = number | string | object;

type Props<T extends ItemValue> = PickerProps<T> & {
  wrapperStyle?: StyleProp<ViewStyle>;
};

function Picker<T extends ItemValue = ItemValue>({
  wrapperStyle,
  style,
  itemStyle,
  children,
  ...pickerProps
}: Props<T>) {
  const { theme } = useUnistyles();
  const itemFont = {
    fontFamily: theme.typography.mono.fontFamily,
    fontSize: theme.typography.mono.fontSize,
    backgroundColor: theme.colors.input.background,
  };

  const items = Children.map(children, (child) => {
    if (!isValidElement<PickerItemProps<T>>(child)) return child;

    return cloneElement(child, {
      style: RNStyleSheet.flatten([itemFont, child.props.style]),
    });
  });

  return (
    <View style={[styles.wrapper, wrapperStyle]}>
      <RNPicker
        style={[styles.shrink, style]}
        itemStyle={RNStyleSheet.flatten([itemFont, itemStyle])}
        {...pickerProps}
      >
        {items}
      </RNPicker>
    </View>
  );
}

Picker.Item = RNPicker.Item;

const styles = StyleSheet.create((theme) => ({
  wrapper: {
    flex: 1,
    height: theme.size.input.height - theme.borderWidth.input * 2,
    overflow: "hidden",
    justifyContent: "center",
    ...(Platform.OS === "web"
      ? {/* The picker package does not provide web styles */}
      : {
          borderColor: theme.colors.input.border,
          borderWidth: theme.borderWidth.input,
          borderRadius: theme.radius.input,
          backgroundColor: theme.colors.input.background,
        }),
  },
  shrink: {
    marginVertical: -12,
  },
}));

export default Picker;
