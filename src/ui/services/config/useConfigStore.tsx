import { useMemo } from 'react';
import { create } from 'zustand';
import { saveData, getData } from '@/services/storage/storage';
import { Server, Endpoint, ServerType } from './configTypes';
import { defaultServers } from './configDefaults';

interface ConfigStore {
  servers: Server[];
  setServers: (servers: Server[]) => void;
  restoreDefaults: () => void;
  loadStore: () => Promise<void>;
}

const STORAGE_KEY = 'quadrupedConfigStore';

export const useConfigStore = create<ConfigStore>((set, get) => ({
  servers: [],

  setServers: (servers: Server[]) => {
    set({ servers });
    saveData(STORAGE_KEY, JSON.stringify({ servers }))
      .then(() => console.log('[Zustand] Store state saved to storage.'))
      .catch(err => console.error('[Zustand] Failed to save store state:', err));
  },

  restoreDefaults: () => {
    const defaultState = { servers: defaultServers };
    set(defaultState);
    saveData(STORAGE_KEY, JSON.stringify(defaultState))
      .then(() => console.log('[Zustand] Defaults restored and saved.'))
      .catch(err => console.error('[Zustand] Failed to save defaults:', err));
  },

  loadStore: async () => {
    try {
      const stored = await getData(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        set(parsed);
        console.log('[Zustand] Config store data loaded from storage.');
      } else {
        console.log('[Zustand] No config store found; loading defaults.');
        get().restoreDefaults();
      }
    } catch (err) {
      console.error('[Zustand] Error loading store:', err);
    }
  },
}));


export const useEndpointByType = (type: ServerType): Endpoint | undefined => {
  const servers = useConfigStore(state => state.servers);

  return useMemo(() => {
    return servers.find(server => server.type === type)?.selectedEndpoint || undefined;
  }, [servers, type]);
};

