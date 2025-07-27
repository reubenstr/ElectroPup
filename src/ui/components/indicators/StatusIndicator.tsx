import { View, Text, StyleSheet, ViewStyle } from 'react-native';
import { Status } from '@/interfaces/messages';

interface IndicatorProps {
    name: string;
    value?: string;
    status?: Status;
    style?: ViewStyle | ViewStyle[]; // Optional style prop
}

export default function Indicator({ name, value, status, style }: IndicatorProps) {

    function getStatusColor(status: Status | undefined): { backgroundColor: string } {
        switch (status) {
            case Status.Standby:
                return { backgroundColor: '#266928' };
            case Status.Active:
                return { backgroundColor: '#4caf50' };
            case Status.Warning:
                return { backgroundColor: '#ff9800' };
            case Status.Critical:
                return { backgroundColor: '#bb0000' };
            case Status.Error:
                return { backgroundColor: '#dd0000' };
            case Status.None:
            default:
                return { backgroundColor: '#aaaaaa' };
        }
    }

    return (
        <View style={[styles.container, getStatusColor(status), style]}>
            <Text style={styles.name}>
                {name}
            </Text>
            {value &&
                <Text style={styles.value}>
                    {value}
                </Text>
            }
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        alignSelf: 'flex-start',
        borderWidth: 1,
        borderColor: 'black',
        padding: 5,
        margin: 5,
        borderRadius: 4,
        alignItems: 'center',
    },
    name: {
        fontWeight: 'bold',
        fontSize: 16,
    },
    value: {
        fontSize: 14,
    }
});
