import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from "expo-secure-store";

/*
    expo-secure-store works only on iOS and Android apps.
    async-storage works with web apps.
*/  

export async function saveData(key: string, value: string): Promise<void> {
    try {
        if (Platform.OS === 'web') {
            await AsyncStorage.setItem(key, value);
        } else {
            await SecureStore.setItemAsync(key, value.toString());
        }
    } catch (error) {
        console.error("Error saving data:", error);
    }
}

export async function getData(key: string): Promise<string | null> {
    try {
        if (Platform.OS === 'web') {
            return await AsyncStorage.getItem(key);
        } else {
            return await SecureStore.getItemAsync(key);
        }
    } catch (error) {
        console.error("Error saving data:", error);
    }

    return null;
}

export async function removeData(key: string): Promise<void> {

    try {
        if (Platform.OS === 'web') {
            await AsyncStorage.removeItem(key);
        } else {
            await SecureStore.deleteItemAsync(key);
        }
    } catch (error) {
        console.error("Error saving data:", error);
    }
}
