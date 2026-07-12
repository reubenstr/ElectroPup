import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { UnistylesRuntime } from "react-native-unistyles";
import { mmkvStorage } from "@/services/storage/storage";

export type ThemeName = "light" | "dark";

interface ThemeStore {
  theme: ThemeName;
  setTheme: (theme: ThemeName) => void;
  showThemeSwitch: boolean;
  setShowThemeSwitch: (showThemeSwitch: boolean) => void;
}

const STORAGE_KEY = "themeStore";

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set) => ({
      theme: UnistylesRuntime.themeName as ThemeName,

      setTheme: (theme) => {
        UnistylesRuntime.setTheme(theme);
        set({ theme });
      },

      showThemeSwitch: true,
      setShowThemeSwitch: (showThemeSwitch) => set({ showThemeSwitch }),
    }),
    {
      name: STORAGE_KEY,
      storage: createJSONStorage(() => mmkvStorage),
      onRehydrateStorage: () => (state) => {
        if (state) {
          UnistylesRuntime.setTheme(state.theme);
        }
      },
    },
  ),
);

export default useThemeStore;
