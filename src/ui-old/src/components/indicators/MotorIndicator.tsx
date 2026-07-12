import { View, Text, StyleSheet } from 'react-native';

interface MotorIndicatorProps {
    name: string;   
    state: boolean;
}

export default function MotorIndicator({ name, state }: MotorIndicatorProps) {

    function stateColors(state: boolean) {   
        return {
            backgroundColor: state ? '#4caf50' : '#aaaaaa'
        };
    }

    return (
        <View style={[styles.container, stateColors(state)]}>
            <Text style={styles.name}>
                {name}
            </Text>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        borderWidth: 1,
        borderColor: 'black',
        padding: 5,      
        borderRadius: 4,
        alignItems: 'center',  
        justifyContent: 'center',
        margin: 2,
    },
    name: {
        fontWeight: 'bold',
        fontSize: 16,
    },   
});