import { StyleSheet } from "react-native-unistyles";
import { Platform } from "react-native";
import { AppTheme } from "@/src/styles/themes";

/* Use in stylesheets, spreadable */

export const createText = (
  theme: AppTheme | any,
  typeSet: keyof AppTheme["typography"],
) => ({
  fontFamily: theme.typography[typeSet].fontFamily,
  fontSize: theme.typography[typeSet].fontSize,
  lineHeight: theme.typography[typeSet].lineHeight,
  letterSpacing: theme.typography[typeSet].letterSpacing,
});

type ShadowType = "glass" | "medium" | "button";

export const createShadow = (theme: AppTheme | any, typeSet: ShadowType) => ({
  boxShadow: theme.shadows[typeSet].boxShadow,
});

type ContainerType = "glass" | "surface" | "card" | "inset";

export const createContainer = (
  theme: AppTheme | any,
  typeSet: ContainerType,
) => ({
  padding: theme.padding[typeSet],
  gap: theme.gap[typeSet],
  backgroundColor: theme.colors.background[typeSet],
  borderRadius: theme.radius[typeSet],
  borderWidth: theme.borderWidth[typeSet],
  borderColor: theme.colors.border[typeSet],
});

/* Plain objects, spreadable */

export const absoluteFillObject = {
  position: "absolute" as const,
  top: 0,
  right: 0,
  bottom: 0,
  left: 0,
};

/* Use directly in component styles prop, do not spread */

export const overlayStyles = StyleSheet.create((theme) => ({
  overlay: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: theme.colors.background.modal,
  },
}));

export const modalStyles = StyleSheet.create((theme) => ({
  container: {
    minHeight: 260,
    minWidth: 360,
    maxWidth: "90%",
    maxHeight: "90%",
    ...createContainer(theme, "glass"),
    ...createShadow(theme, "glass"),
    padding: theme.padding.modal,

  },
}));

export const inputStyles = StyleSheet.create((theme) => ({
  input: {
    flexGrow: 1,
    height: theme.size.input.height,
    paddingHorizontal: theme.padding.input.horizontal,
    paddingVertical: theme.padding.input.vertical,
    color: theme.colors.text.primary,
    backgroundColor: theme.colors.input.background,
    borderColor: theme.colors.input.border,
    borderRadius: theme.radius.generalButton,
    borderWidth: theme.borderWidth.input,
    overflow: "hidden",
    ...createText(theme, "mono"),
    ...(Platform.OS === "web"
      ? {
          outlineColor: theme.colors.input.borderFocus,
          outlineStyle: "solid" as const,
          outlineWidth: 0,
        }
      : {}),
  },
}));

export const tabStyles = StyleSheet.create((theme) => ({
  container: {
    flexDirection: "row",
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border.accent,
    marginBottom: 10,
  },
  tab: {
    flex: 1,
    paddingBottom: 10,
    alignItems: "center",
    borderBottomWidth: 2,
    borderBottomColor: "transparent",
  },
  activeTab: {
    borderBottomColor: theme.colors.selected,
  },
  tabText: {
    color: theme.colors.text.secondary,
    ...createText(theme, "body"),
  },
  activeTabText: {
    color: theme.colors.text.primary,
  },
}));

export const tabStylesFolder = StyleSheet.create((theme) => ({
  controls: {
    flexDirection: "row",  
    gap: 2,
  }, 
  controlsWithStyle: {
    flexDirection: "row",
    borderColor: theme.colors.border.accent,
    borderBottomWidth: 2,
    gap: 2,
  }, 
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: theme.colors.background.card,
  },
  content: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    width: "100%",
  },
  tab: {
    paddingVertical: 8,
    paddingHorizontal: 13,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: theme.colors.background.card,
    borderTopLeftRadius: theme.radius.generalButton,
    borderTopRightRadius: theme.radius.generalButton,
    borderColor: theme.colors.divider,
    borderWidth: 1,
    borderBottomWidth: 0,
  },
  activeTab: {
    backgroundColor: theme.colors.selected,
  },
  tabText: {
    color: theme.colors.text.secondary,
    ...createText(theme, "body"),
  },
  activeTabText: {
    color: theme.colors.text.inverse,
    ...createText(theme, "body"),
    fontFamily: "OrbitronBold",
  },
}));

export const checkboxStyles = StyleSheet.create((theme) => ({
  container: {
    marginLeft: 4,
    marginTop: 4,
    width: "100%",
  },
  checkboxContainer: {
    alignItems: "center",
    flexDirection: "row",
  },
  checkbox: {
    alignItems: "center",
    backgroundColor: theme.colors.input.background,
    borderColor: theme.colors.border.accent,
    borderRadius: 4,
    borderWidth: 1.5,
    height: 22,
    justifyContent: "center",
    marginRight: 10,
    width: 22,
  },
  checked: {
    backgroundColor: theme.colors.input.background,
    borderColor: theme.colors.text.primary,
  },
  checkmark: {
    color: theme.colors.text.primary,
    fontWeight: "bold",
  },
  label: {
    color: theme.colors.text.primary,
    fontSize: 14,
  },
}));
