import { View, Text, StyleSheet } from 'react-native';

interface ContactIndicatorProps {
    name: string;   
    state?: boolean;
}

export default function ContactIndicator({ name, state }: ContactIndicatorProps) {

    function stateColors(state?: boolean) {
        return {
            backgroundColor: state ? '#00ff00' : '#aaaaaa'
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
        borderRadius: 5,
        margin: 2,
        alignItems: 'center',  
        justifyContent: 'center',
    },
    name: {
        fontWeight: 'bold',
        fontSize: 16,
  
    },   
});