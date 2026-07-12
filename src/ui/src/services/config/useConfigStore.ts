import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import { mmkvStorage } from "@/services/storage/storage";
import { Endpoint, EndpointConfig } from "./configTypes";
import { defaultEndpoints } from "./configDefaults";

const STORAGE_KEY = "configStore";

interface ConfigStore {
  config: EndpointConfig;

  setSelection: (index: number) => void;
  addEndpoint: (endpoint: Endpoint) => void;
  updateEndpoint: (index: number, endpoint: Endpoint) => void;
  removeEndpoint: (index: number) => void;

  restoreDefaults: () => void;
}

const clampSelection = (selection: number, length: number) =>
  Math.max(0, Math.min(selection, length - 1));

export const useConfigStore = create<ConfigStore>()(
  persist(
    (set) => ({
      config: defaultEndpoints,

      setSelection: (index) =>
        set(({ config }) => ({
          config: {
            ...config,
            selection: clampSelection(index, config.endpoints.length),
          },
        })),

      addEndpoint: (endpoint) =>
        set(({ config }) => ({
          config: {
            endpoints: [...config.endpoints, endpoint],
            selection: config.endpoints.length,
          },
        })),

      updateEndpoint: (index, endpoint) =>
        set(({ config }) => ({
          config: {
            ...config,
            endpoints: config.endpoints.map((ep, i) =>
              i === index ? endpoint : ep,
            ),
          },
        })),

      removeEndpoint: (index) =>
        set(({ config }) => {
          const endpoints = config.endpoints.filter((_, i) => i !== index);
          const selection =
            index < config.selection ? config.selection - 1 : config.selection;

          return {
            config: {
              endpoints,
              selection: clampSelection(selection, endpoints.length),
            },
          };
        }),

      restoreDefaults: () => set({ config: defaultEndpoints }),
    }),
    {
      name: STORAGE_KEY,
      storage: createJSONStorage(() => mmkvStorage),
    },
  ),
);

export default useConfigStore;
