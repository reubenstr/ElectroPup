import { useRouter, usePathname } from "expo-router";
import { Pressable, Text, View } from "react-native";
import { StyleSheet } from "react-native-unistyles";
import { createShadow, createText } from "@/styles/themeComponents";

const NAV_ITEMS = [
  { label: "Plot", href: "/" },
  { label: "Data", href: "/data" },
  { label: "Settings", href: "/settings" },
  { label: "About", href: "/about" },
] as const;

export function TopNav() {
  const router = useRouter();
  const pathname = usePathname();

  return (
    <View style={styles.header}>
      <Pressable accessibilityRole="link" onPress={() => router.navigate("/")}>
        <Text style={styles.appName}>ElectroPup</Text>
      </Pressable>

      <View style={styles.nav}>
        {NAV_ITEMS.map(({ label, href }) => {
          const isActive = pathname === href;

          return (
            <Pressable
              key={href}
              accessibilityRole="link"
              accessibilityState={{ selected: isActive }}
              onPress={() => router.navigate(href)}
              style={styles.navButton(isActive)}
            >
              <Text style={styles.navLabel(isActive)}>{label}</Text>
            </Pressable>
          );
        })}
      </View>

    </View>
  );
}

const styles = StyleSheet.create((theme) => ({
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: theme.gap.surface,
    padding: theme.padding.surface,
    backgroundColor: theme.colors.background.surface,
    borderWidth: theme.borderWidth.surface,
    borderColor: theme.colors.border.surface,
    borderRadius: theme.radius.surface,
    zIndex: theme.zIndex.control,
    ...createShadow(theme, "medium"),
  },
  nav: {
    flexDirection: "row",
    gap: theme.gap.control,
  },
  navButton: (isActive: boolean) => ({
    alignItems: "center",
    justifyContent: "center",
    minHeight: theme.size.control.minHeight,
    minWidth: theme.size.control.minWidth,
    paddingHorizontal: theme.padding.control.horizontal,
    paddingVertical: theme.padding.control.vertical,
    borderRadius: theme.radius.control,
    borderWidth: theme.borderWidth.control,
    borderColor: theme.colors.button.border,
    backgroundColor: isActive
      ? theme.colors.selected
      : theme.colors.button.background,
  }),
  navLabel: (isActive: boolean) => ({
    color: isActive ? theme.colors.text.inverse : theme.colors.button.text,
    ...createText(theme, "body"),
  }),
  appName: {
    color: theme.colors.text.primary,
    ...createText(theme, "header1"),
  },
}));
