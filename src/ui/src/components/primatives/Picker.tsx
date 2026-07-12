import { Children, cloneElement, createElement, isValidElement } from "react";
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

    /* The package's web PickerItem renders an <option> but forwards only
       `color`, dropping `style`. Without a background the option falls back to
       the browser's white popup, so theme text is unreadable on it. Emit the
       <option> directly to control both colors. */
    if (Platform.OS === "web") {
      const { label, value, color, enabled } = child.props;

      return createElement(
        "option",
        {
          value: value as string | number,
          disabled: enabled === false || undefined,
          style: {
            color: color ?? theme.colors.text.primary,
            backgroundColor: theme.colors.input.background,
            fontFamily: theme.typography.mono.fontFamily,
            fontSize: theme.typography.mono.fontSize,
          },
        },
        label,
      );
    }

    return cloneElement(child, {
      color: child.props.color ?? theme.colors.text.primary,
      style: RNStyleSheet.flatten([itemFont, child.props.style]),
    });
  });

  return (
    <View style={[styles.wrapper, wrapperStyle]}>
      <RNPicker
        style={[styles.picker, style]}
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
      ? {/* The select is styled directly; see `picker` below. */}
      : {
          borderColor: theme.colors.input.border,
          borderWidth: theme.borderWidth.input,
          borderRadius: theme.radius.input,
          backgroundColor: theme.colors.input.background,
        }),
  },
  /* On web the package renders a bare <select> and drops `itemStyle`, so the
     element gets no color or font of its own. Style it here instead. */
  picker: {
    ...(Platform.OS === "web"
      ? {
          height: "100%",
          color: theme.colors.text.primary,
          backgroundColor: theme.colors.input.background,
          borderColor: theme.colors.input.border,
          borderWidth: theme.borderWidth.input,
          borderRadius: theme.radius.input,
          paddingHorizontal: theme.padding.input.horizontal,
          fontFamily: theme.typography.mono.fontFamily,
          fontSize: theme.typography.mono.fontSize,
        }
      : { marginVertical: -12 }),
  },
}));

export default Picker;
