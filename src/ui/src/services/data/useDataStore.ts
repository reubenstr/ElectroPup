import { create } from "zustand";
import { Data } from "@/services/data/dataTypes";

export type ConnectionStatus = "disconnected" | "connecting" | "connected";

interface DataStore {
  data: Data | undefined;
  status: ConnectionStatus;

  setData: (data: Data) => void;
  clearData: () => void;
  setStatus: (status: ConnectionStatus) => void;
}

export const useDataStore = create<DataStore>((set) => ({
  data: undefined,
  status: "disconnected",

  setData: (data) => set({ data }),

  clearData: () => set({ data: undefined }),

  setStatus: (status) =>
    set((state) => ({
      status,     
      data: status === "connected" ? state.data : undefined,
    })),
}));

export const useConnected = () =>
  useDataStore((state) => state.status === "connected");

export default useDataStore;
