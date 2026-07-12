import { Link, Stack } from 'expo-router';
import { View, Text, StyleSheet } from 'react-native';

import Viewer from './viewer';

export default function HomeScreen() {
    return (
        <View style={styles.container}>      
            <Viewer />
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        alignItems: 'center',
        justifyContent: 'center',  
    },
});