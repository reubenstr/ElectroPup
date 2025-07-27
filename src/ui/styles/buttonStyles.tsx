import { StyleSheet, Platform } from "react-native";
import Colors from "@/styles/colors"


export const ControlStyles = StyleSheet.create({
    primary: {
        backgroundColor: '#3434dd',
    },
    success: {
        backgroundColor: '#28a745',
    },
    danger: {
        backgroundColor: '#dc1313',
    },
});

export const ButtonStyles = StyleSheet.create({
    container: {
        flex: 1,
        justifyContent: 'center',
        alignItems: 'center',
    },
    button: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: Colors.shared.primary,
        paddingVertical: 8,
        paddingHorizontal: 10,
        borderRadius: 6,
        margin: 3
    },
    primary: {
        backgroundColor: Colors.shared.primary,
    },
    success: {
        backgroundColor: Colors.shared.success,
    },
    danger: {
        backgroundColor: Colors.shared.danger,
    },
    critical: {
        backgroundColor: '#db3434',
      },
    cancel: {
        backgroundColor: '#bbbbbb',
    },
    icon: {
        marginLeft: 5,
        marginRight: 5,
    },
    iconCircle: {
        marginLeft: 5,
        marginRight: 5,
        width: 40,
        height: 40,
        padding: 8,
        borderRadius: 20,
        color: Colors.dark.foreground,
        backgroundColor: Colors.dark.background,
        alignItems: 'center',
        justifyContent: 'center',
    },
    center: {
        alignItems: 'center',
        justifyContent: 'center',
    },
    text: {
        color: Colors.dark.text,
        fontWeight: 'bold',
        fontSize: 16,      
        fontFamily: Platform.select({
            ios: '-apple-system',
            android: 'Roboto',
            default: 'sans-serif',
        }),
        textTransform: "uppercase"
    },  
});

export const IconStyles = StyleSheet.create({
    container: {        
        paddingVertical: 8,
        paddingHorizontal: 10,
        borderRadius: 6,
        margin: 3
    },   
    icon: {
        color: 'white',   
        fontSize: 18,  
    },   
});