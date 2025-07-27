const tintColorLight = '#2f95dc';
const tintColorDark = '#fff';
const shadeLight = '#ECECED';
const accentLight = '#57A5BE';
const accentDark = '#8B4F41';
const shadeDark = '#10131E';
const colorPrimary = '#3434dd';
const colorInfo = '#10c31d';
const colorSuccess = '#7eb14f';
const colorWarning = '#fba117';
const colorError = '#f44336';
const colorCritical = '#d42316';
const colorUnknown = '#444444';

export default {
  shared: {
    primary: colorPrimary,
    info: colorInfo,
    success: colorSuccess,
    warning: colorWarning,
    danger: colorError,
    error: colorError,
    critical: colorCritical,
    unknown: colorUnknown,
  },
  light: {
    text: shadeDark,
    foreground: shadeDark,
    background: shadeLight,
    accent: accentLight,
    tint: tintColorLight,
    tabIconDefault: '#ccc',
    tabIconSelected: tintColorLight,
  },
  dark: {
    text: shadeLight,
    foreground: shadeLight,
    background: shadeDark,
    accent: accentDark,
    tint: tintColorDark,
    tabIconDefault: '#ccc',
    tabIconSelected: tintColorDark,
  },
};
