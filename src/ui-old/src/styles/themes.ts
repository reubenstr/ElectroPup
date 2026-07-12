import { Platform } from "react-native";

const isWeb = Platform.OS === "web";

const black = "#000000";
const white = "#ffffff";

const colorAction = "#0079e4";
const colorInfo = "#f5f5f5";
const colorSuccess = "#7eb14f";
const colorWarning = "#fbd117";
const colorDanger = "#f72e20";
const colorError = "#f72e20";
const colorCritical = "#d42316";
const colorUnknown = "#555555";

const colorSelected = "#f49f00";
const colorPending = "#815502";

const accentLight = "#747474";
const accentLightSecondary = "#747474";
const accentDark = "#6c6c6c";
const accentDarkSecondary = "#414141";

const textPrimaryDark = "#dfdfdf";
const textSecondaryDark = "#a0a0a0";
const textDisabledDark = "#bababa";
const textInverseDark = "#1f1f1f";

const textPrimaryLight = "#3f3f3f";
const textSecondaryLight = "#666666";
const textDisabledLight = "#4a4a4a";
const textInverseLight = "#ffffff";

const buttonBackgroundLight = "rgba(217, 217, 217, 0.75)";
const buttonBackgroundDark = "rgba(25, 25, 25, 0.75)";

export const sharedColors = {
  mapFeatures: {
    drawing: {
      poi: "#57fc5799",
      keepins: "#8383f8ff",
      keepouts: "#f86b6bff",
      unknown: "#000000",
    },
    onMap: {
      poi: "#FF9500",
      keepins: "#007AFF",
      keepouts: "#FF3B30",
      primary: "#006EDB",
      unknown: "#000000",
    },
  },
} as const;

const lightColors = {
  text: {
    primary: textPrimaryLight,
    inverse: textInverseLight,
    secondary: textSecondaryLight,
    disabled: textDisabledLight,

    action: colorAction,
    info: colorInfo,
    success: colorSuccess,
    warning: colorWarning,
    danger: colorError,
    error: colorError,
    critical: colorCritical,
    unknown: colorUnknown,
    selected: colorSelected,
  },

  selected: colorSelected,
  pending: colorPending,

  divider: accentLight,

  border: {
    glass: black,
    surface: black,
    card: black,
    inset: black,
    accent: accentDark,
    selected: colorSelected,
    input: accentDark,
  },

  background: {
    glass: "rgba(230, 230, 230, 0.75)",
    surface: "rgba(215, 215, 215, 0.95)",
    card: "rgba(200, 200, 200, 0.95)",
    inset: "rgba(185, 185, 185, 0.95)",
    overlay: "rgba(76, 76, 76, 0.6)",
    modal: "rgba(76, 76, 76, 0.90)",
    opaque: white,
  },

  button: {
    text: textPrimaryLight,
    inverse: textPrimaryLight,
    hover: colorSelected,
    active: colorSelected,
    icon: textPrimaryLight,
    border: black,
    background: buttonBackgroundLight,
    disabled: {
      icon: textPrimaryLight,
      text: textDisabledLight,
      background: buttonBackgroundLight,
      border: textDisabledLight,
    },
    variants: {
      action: colorAction,
      info: colorInfo,
      success: colorSuccess,
      warning: colorWarning,
      danger: colorDanger,
      navigation: black,
    },
  },

  joystick: {
    feature: {
      pad: "rgba(25, 25, 25, 0.75)",
      crosshair: "rgba(100, 100, 100, 0.75)",
      stick: "rgba(125, 125, 125, 0.75)",
      knob: "rgba(150, 150, 150, 0.75)",
    },
    border: {
      pad: "rgba(25, 25, 25, 0.75)",
      crosshair: "rgba(100, 100, 100, 0.75)",
      stick: "rgba(125, 125, 125, 0.75)",
      knob: "rgba(150, 150, 150, 0.75)",
    },
  },

  input: {
    label: "#c4c4c4",
    placeholder: "#888888",
    text: textPrimaryDark,
    disabledtext: "#242424",
    border: "#353535",
    borderFocus: colorSelected,
    background: "#a6a6a6",
    disabledBackground: "#242424",
  },

  mapFeatures: sharedColors.mapFeatures,
} as const;

const darkColors = {
  text: {
    primary: textPrimaryDark,
    inverse: textInverseDark,
    secondary: textSecondaryDark,
    disabled: textDisabledDark,

    action: colorAction,
    info: colorInfo,
    success: colorSuccess,
    warning: colorWarning,
    danger: colorError,
    error: colorError,
    critical: colorCritical,
    unknown: colorUnknown,
    selected: colorSelected,
  },

  selected: colorSelected,
  pending: colorPending,

  divider: accentLight,

  border: {
    glass: black,
    surface: black,
    card: black,
    inset: black,
    accent: accentDark,
    selected: colorSelected,
    input: accentDark,
  },

  background: {
    glass: "rgba(54, 54, 54, 0.75)",
    surface: "rgba(85, 85, 85, 0.95)",
    card: "rgba(75, 75, 75, 0.95)",
    inset: "rgba(65, 65, 65, 0.95)",
    overlay: "rgba(25, 25, 25, 0.6)",
    modal: "rgba(25, 25, 25, 0.90)",
    opaque: black,
  },

  button: {
    text: textPrimaryDark,
    inverse: textInverseDark,
    hover: colorSelected,
    active: colorSelected,
    icon: textPrimaryDark,
    border: black,
    background: buttonBackgroundDark,
    disabled: {
      icon: textSecondaryDark,
      text: textDisabledLight,
      background: buttonBackgroundDark,
      border: textDisabledLight,
    },
    variants: {
      action: colorAction,
      info: colorInfo,
      success: colorSuccess,
      warning: colorWarning,
      danger: colorDanger,
      navigation: black,
    },
  },

  joystick: {
    feature: {
      pad: "rgba(25, 25, 25, 0.75)",
      crosshair: "rgba(100, 100, 100, 0.75)",
      stick: "rgba(75, 75, 75, 0.75)",
      knob: "rgba(100, 100, 100, 0.75)",
    },
    border: {
      pad: "black",
      crosshair: "rgba(100, 100, 100, 0.95)",
      stick: "rgba(75, 75, 75, 0.95)",
      knob: "rgba(125, 125, 125, 0.85)",
    },
  },

  input: {
    label: "#c4c4c4",
    placeholder: "#888888",
    text: textPrimaryDark,
    disabledtext: "#242424",
    border: "#8b8b8b",
    borderFocus: colorSelected,
    background: "#333333",
    disabledBackground: "#242424",
  },

  mapFeatures: sharedColors.mapFeatures,
} as const;

/* Layout */

const layout = {
  width: {
    leftColumn: isWeb ? 120 : 80, // View selector
    rightColumn: isWeb ? 120 : 80, // Platform selector
    navigation: isWeb ? 160 : 120, // Config selector, info selector
  },
  padding: isWeb ? 15 : 10, // Padding around major elements
} as const;

/* Sizes */

const padding = {
  glass: isWeb ? 15 : 10,
  surface: isWeb ? 15 : 10,
  card: isWeb ? 12 : 8,
  inset: isWeb ? 10 : 5,
  modal: isWeb ? 30 : 20,

  generalButton: {
    horizontal: isWeb ? 10 : 5,
    vertical: isWeb ? 8 : 8,
  },
  input: {
    horizontal: isWeb ? 10 : 10,
    vertical: isWeb ? 10 : 10,
  },
} as const;

const gap = {
  glass: isWeb ? 8 : 6,
  surface: isWeb ? 10 : 6,
  card: isWeb ? 8 : 4,
  inset: isWeb ? 8 : 4,
  generalButton: isWeb ? 10 : 6,
  input: isWeb ? 10 : 8,
};

const size = {
  icons: {
    viewSelector: isWeb ? 30 : 24,
    platformSelector: isWeb ? 40 : 35,
    generalButton: isWeb ? 20 : 16,
  },
  input: {
    height: isWeb ? 40 : 36,
  },
  generalButton: {
    minHeight: 36,
    minWidth: 40,
  },
  viewSelector: {
    minHeight: 40,
    minWidth: 40,
  },
  joystick: {
    pad: 120,
    stick: 30,
    knob: 60,
  },

  // TODO: move other icons here, add to style guide
  icon: {
    viewSelector: 24,
    platformSelector: 40,
    cameraSelector: 24,
  },
} as const;

/* Textures */

const borderWidth = {
  glass: 2,
  surface: 2,
  card: 1,
  inset: 1,
  generalButton: isWeb ? 2 : 1,
  input: 1,
  divider: 1,

  joystick: {
    pad: 3,
    crosshair: 2,
    stick: 2,
    knob: 3,
  },
} as const;

const radius = {
  glass: 5,
  surface: 5,
  card: 5,
  inset: 5,
  generalButton: 5,
  input: 4,
} as const;

/* Typography */

const fontFamily = {
  regular: Platform.select({
    ios: "System",
    android: "sans-serif",
    web: "system-ui",
    default: "System",
  }),
  medium: Platform.select({
    ios: "System",
    android: "sans-serif-medium",
    web: "system-ui",
    default: "System",
  }),
  semiBold: Platform.select({
    ios: "System",
    android: "sans-serif-medium",
    web: "system-ui",
    default: "System",
  }),
  bold: Platform.select({
    ios: "System",
    android: "sans-serif-bold",
    web: "system-ui",
    default: "System",
  }),
  mono: Platform.select({
    ios: "Menlo",
    android: "monospace",
    web: "monospace",
    default: "monospace",
  }),
} as const;

const typography = {
  header1: {
    fontFamily: "OrbitronMedium",
    fontSize: isWeb ? 20 : 18,
    lineHeight: 22,
    letterSpacing: 0,
  },
  header2: {
    fontFamily: "OrbitronMedium",
    fontSize: isWeb ? 18 : 16,
    lineHeight: 18,
    letterSpacing: 0,
  },
  body: {
    fontFamily: "OrbitronRegular",
    fontSize: isWeb ? 16 : 14,
    lineHeight: 18,
    letterSpacing: 0,
  },
  secondary: {
    fontFamily: "OrbitronRegular",
    fontSize: isWeb ? 14 : 12,
    lineHeight: 18,
    letterSpacing: 0,
  },
  mono: {
    fontFamily: fontFamily.mono,
    fontSize: isWeb ? 16 : 14,
    lineHeight: 18,
    letterSpacing: 0,
  },
  generalButton: {
    fontFamily: "OrbitronMedium",
    fontSize: isWeb ? 18 : 14,
    lineHeight: isWeb ? 22 : 18,
    letterSpacing: 0,
  },
} as const;

/* Miscellaneous */

const shadows = {
  glass: {
    boxShadow: "0px 3px 3.35px rgba(0,0,0,0.27)",
  },
  medium: {
    boxShadow: "0px 2px 2.62px rgba(0,0,0,0.23)",
  },
  button: {
    boxShadow: "0px 1px 1px rgba(0,0,0,0.18)",
  },
} as const;

const zIndex = {
  base: 0,
  manualControl: 500,
  dropdown: 1000,
  tooltip: 1500,
  menu: 1750,
  modal: 2000,
  popover: 3000,
  toast: 4000,
  zenith: 9999,
} as const;

const opacity = {
  disabled: 0.5,
  pressed: 0.75,
  overlay: 0.6,
} as const;

/* Theme exports */

export const lightDeviceTheme = {
  colors: lightColors,
  layout,
  padding,
  gap,
  size,
  borderWidth,
  radius,
  typography,
  shadows,
  zIndex,
  opacity,
};

export const darkDeviceTheme = {
  colors: darkColors,
  layout,
  padding,
  gap,
  size,
  borderWidth,
  radius,
  typography,
  shadows,
  zIndex,
  opacity,
};

export type AppTheme = typeof lightDeviceTheme;
