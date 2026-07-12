import { createMMKV } from 'react-native-mmkv';
import type { StateStorage } from 'zustand/middleware';

/*
  react-native-mmkv provides fast, synchronous storage.
  On web, MMKV uses browser storage behavior rather than native MMKV.
*/

// Create a default MMKV instance
export const storage = createMMKV();

// Primary functions for saving, retrieving, and removing data
export function saveData(key: string, value: string): void {
  try {
    storage.set(key, value);
  } catch (error) {
    console.error('Error saving data:', error);
  }
}

export function getData(key: string): string | undefined {
  try {
    return storage.getString(key);
  } catch (error) {
    console.error('Error getting data:', error);
    return undefined;
  }
}

export function removeData(key: string): void {
  try {
    storage.remove(key);
  } catch (error) {
    console.error('Error removing data:', error);
  }
}

// MMKV storage adapter for Zustand persist
export const mmkvStorage: StateStorage = {
  getItem: (name: string): string | null => {
    const value = storage.getString(name);
    return value ?? null;
  },

  setItem: (name: string, value: string): void => {
    storage.set(name, value);
  },

  removeItem: (name: string): void => {
    storage.remove(name);
  },
};

// Additional helper functions for other data types
export function saveBoolean(key: string, value: boolean): void {
  try {
    storage.set(key, value);
  } catch (error) {
    console.error('Error saving boolean:', error);
  }
}

export function getBoolean(key: string): boolean | undefined {
  try {
    return storage.getBoolean(key);
  } catch (error) {
    console.error('Error getting boolean:', error);
    return undefined;
  }
}

export function saveNumber(key: string, value: number): void {
  try {
    storage.set(key, value);
  } catch (error) {
    console.error('Error saving number:', error);
  }
}

export function getNumber(key: string): number | undefined {
  try {
    return storage.getNumber(key);
  } catch (error) {
    console.error('Error getting number:', error);
    return undefined;
  }
}

export function getAllKeys(): string[] {
  try {
    return storage.getAllKeys();
  } catch (error) {
    console.error('Error getting all keys:', error);
    return [];
  }
}

export function clearAll(): void {
  try {
    storage.clearAll();
  } catch (error) {
    console.error('Error clearing all data:', error);
  }
}