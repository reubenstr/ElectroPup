import { Platform } from "react-native";

const isWeb = Platform.OS === "web";

const black = "#000000";

const colorAction = "#0079e4";
const colorInfo = "#f5f5f5";
const colorSuccess = "#7eb14f";
const colorWarning = "#fbd117";
const colorDanger = "#f72e20";
const colorError = "#f72e20";

const colorSelected = "#105be6";

const accentLight = "#747474";
const accentDark = "#6c6c6c";

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
const indicatorNeutral = "#8a8a8a";

/* Synthwave retro '90s palette — neon green and electric yellow now lead,
   with hot pink, cyan, and orange in supporting roles, and purple kept as
   a secondary accent (text, dividers) against deep indigo/violet-black
   surfaces. */
const synthHotPink = "#ff2ec4";
const synthCyan = "#00f0ff";
const synthPurple = "#b967ff";
const synthMagenta = "#ff00aa";
const synthOrange = "#ff7a18";
const synthYellow = "#ffe700";
const synthGreen = "#05ffa1";
const synthLimeGreen = "#aefc00";
const synthGoldYellow = "#ffc400";
const synthBlueViolet = "#7b2ff7";

const synthTextPrimary = "#f5e8ff";
const synthTextSecondary = "#c9a4f5";
const synthTextDisabled = "#6b5480";
const synthTextInverse = "#170a2e";

const synthAccent = "#a24bd6";
const synthButtonBackground = "rgba(43, 15, 74, 0.75)";
const synthIndicatorNeutral = "#6b5480";


/* `active`/`on` use `colorSelected` (the same vivid green as button.active and
   the nav's selected tab) rather than the variants.success olive green, which
   reads as muted once it fills a whole indicator instead of a thin border. */
const statusColors = {
  none: indicatorNeutral,
  standby: colorAction,
  active: colorSuccess,
  warning: colorWarning,
  critical: colorDanger,
  error: colorError,
};

const indicatorColors = {
  on: colorSuccess,
  off: indicatorNeutral,
  text: textInverseDark,
};

const robotColorsLight = {
  sim: { body: "#00d9c0", joint: "#05ffa1", foot: "#aefc00" },
  live: { body: "#d6008c", joint: "#ff2ec4", foot: "#ff5fd8" },
  support: synthGoldYellow,
  ring: synthYellow,
  transition: synthOrange,
  trajectory: { start: synthLimeGreen, end: synthCyan },
  hold: { start: synthMagenta, end: "#7a0050" },
  line: "#665288",
};

const robotColorsDark = {
  sim: { body: "#00a400", joint: "#00cd00", foot: "#0aff0a" },
  live: { body: "#b00000", joint: "#d10000", foot: "#ff3b30" },
  support: "#ffa801",
  ring: "#dddd00",
  transition: "#ffa801",
  trajectory: { start: "#ff0000", end: "#0000ff" },
  hold: { start: "#ff0000", end: "#9e0000" },
  line: "#000000",
};

const lightColors = {
  text: {
    primary: synthTextPrimary,
    inverse: synthTextInverse,
    secondary: synthTextSecondary,
    disabled: synthTextDisabled,

    action: synthLimeGreen,
    info: synthPurple,
    success: synthGreen,
    warning: synthYellow,
    danger: synthMagenta,
    error: synthMagenta,
  },

  selected: synthGoldYellow,

  divider: synthAccent,

  border: {
    surface: synthBlueViolet,
    card: synthGreen,
    inset: synthCyan,
    selected: synthYellow,
    input: synthAccent,
  },

  background: {
    surface: "rgba(24, 10, 46, 0.95)",
    card: "rgba(35, 14, 64, 0.95)",
    inset: "rgba(18, 6, 38, 0.95)",
    overlay: "rgba(10, 3, 26, 0.75)",
    modal: "rgba(15, 5, 36, 0.92)",
  },

  button: {
    text: synthTextPrimary,
    inverse: synthTextInverse,
    hover: synthYellow,
    active: synthGreen,
    icon: synthTextPrimary,
    border: synthGreen,
    background: synthButtonBackground,
    disabled: {
      icon: synthTextDisabled,
      text: synthTextDisabled,
      background: synthButtonBackground,
      border: synthTextDisabled,
    },
    variants: {
      action: synthLimeGreen,
      info: synthPurple,
      success: synthGreen,
      warning: synthYellow,
      danger: synthMagenta,
      navigation: synthBlueViolet,
    },
  },

  joystick: {
    feature: {
      pad: "rgba(35, 14, 64, 0.75)",
      crosshair: "rgba(185, 103, 255, 0.75)",
      stick: "rgba(5, 255, 161, 0.75)",
      knob: "rgba(255, 231, 0, 0.75)",
    },
    border: {
      pad: "rgba(185, 103, 255, 0.75)",
      crosshair: "rgba(0, 240, 255, 0.75)",
      stick: "rgba(5, 255, 161, 0.75)",
      knob: "rgba(255, 196, 0, 0.75)",
    },
  },

  input: {
    label: synthTextSecondary,
    placeholder: "#7a5c9e",
    text: synthTextPrimary,
    disabledtext: "#3a2a52",
    border: synthAccent,
    borderFocus: synthGreen,
    background: "#2b0f4a",
    disabledBackground: "#1c0a30",
  },

  status: statusColors,
  indicator: indicatorColors,
  robot: robotColorsLight,
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
  },

  selected: colorSelected,

  divider: accentLight,

  border: {
    surface: black,
    card: black,
    inset: black,
    selected: colorSelected,
    input: accentDark,
  },

  background: {
    surface: "rgba(85, 85, 85, 0.95)",
    card: "rgba(75, 75, 75, 0.95)",
    inset: "rgba(65, 65, 65, 0.95)",
    overlay: "rgba(25, 25, 25, 0.6)",
    modal: "rgba(25, 25, 25, 0.90)",
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

  status: statusColors,
  indicator: indicatorColors,
  robot: robotColorsDark,
} as const;


/* Sizes */

const padding = {
  surface: isWeb ? 15 : 10,
  card: isWeb ? 12 : 8,
  inset: isWeb ? 10 : 5,
  modal: isWeb ? 30 : 20,

  control: {
    horizontal: isWeb ? 10 : 5,
    vertical: isWeb ? 8 : 8,
  },
  input: {
    horizontal: isWeb ? 10 : 10,
    vertical: isWeb ? 10 : 10,
  },
} as const;

const gap = {
  surface: isWeb ? 10 : 6,
  card: isWeb ? 8 : 4,
  inset: isWeb ? 8 : 4,
  control: isWeb ? 10 : 6,
  input: isWeb ? 10 : 8,
};

const size = {
  content: {
    maxWidth: 1280,
  },
  input: {
    height: isWeb ? 40 : 36,
  },
  control: {
    minHeight: 36,
    minWidth: 40,
    icon: isWeb ? 20 : 16,
  },
  joystick: {
    pad: 120,
    stick: 30,
    knob: 60,
  },
} as const;

/* Textures */

const borderWidth = {
  surface: 2,
  card: 1,
  inset: 1,
  control: isWeb ? 2 : 1,
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
  surface: 5,
  card: 5,
  inset: 5,
  control: 5,
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
    fontSize: isWeb ? 22 : 18,
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
  control: {
    fontFamily: "OrbitronRegular",
    fontSize: isWeb ? 16 : 14,
    lineHeight: 18,
    letterSpacing: 0,
  },
  mono: {
    fontFamily: fontFamily.mono,
    fontSize: isWeb ? 16 : 14,
    lineHeight: 18,
    letterSpacing: 0,
  },
} as const;

/* Miscellaneous */

const shadows = {
  large: {
    boxShadow: "0px 3px 3.35px rgba(0,0,0,0.27)",
  },
  medium: {
    boxShadow: "0px 2px 2.62px rgba(0,0,0,0.23)",
  },
  small: {
    boxShadow: "0px 1px 1px rgba(0,0,0,0.18)",
  },
} as const;

const zIndex = {
  base: 0,
  control: 500,
  dropdown: 1000,
  tooltip: 1500,
  menu: 1750,
  modal: 2000,
  popover: 3000,
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