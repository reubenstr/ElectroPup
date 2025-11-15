import React, { useEffect, useState, useRef } from "react";
import { Modal, View, Text, StyleSheet, ScrollView, TouchableOpacity, TextInput } from "react-native";
import { Picker } from '@react-native-picker/picker';
import { ControlStyles, ButtonStyles, IconStyles } from "@/styles/buttonStyles";
import Icon from 'react-native-vector-icons/FontAwesome';
import AddServerEndpointModal from './modals/AddServerEndpointModal'
import ConfirmationModal from './modals/ConfirmationModal'
import { useConfigStore } from '@/services/config/useConfigStore'
import { Server, Endpoint } from "@/services/config/configTypes";

export default function ServerSelector() {
    const configStore = useConfigStore();
    const [selectedServer, setSelectedServer] = useState<Server>({} as Server);
    const [selectedEndpoint, setSelectedEndpoint] = useState<Endpoint>({} as Endpoint);
    const [selectedOperation, setSelectedOperation] = useState<'add' | 'edit'>('add');

    const [displayEndpointModel, setDisplayEndpointModel] = useState(false);
    const [displayConfirmationModal, setDisplayConfirmationModal] = useState(false);

    const handleEndpointChange = (server: Server, selectedAddress: string) => {

        const updatedServers = configStore.servers.map(s => {
            if (s.type === server.type) {
                const newSelectedEndpoint = s.endpoints.find(ep => ep.address === selectedAddress);
                return {
                    ...s,
                    selectedEndpoint: newSelectedEndpoint || s.endpoints[0],
                };
            }
            return s;
        });

        configStore.setServers(updatedServers);
    };

    const handleOnSubmit = (server: Server, endpoint: Endpoint) => {
        if (selectedOperation === 'add') {
            const updatedServers = configStore.servers.map(s => {
                if (s.type === server.type) {
                    return {
                        ...s,
                        endpoints: [...s.endpoints, endpoint],
                    };
                }
                return s;
            });
            configStore.setServers(updatedServers);
        } else if (selectedOperation === 'edit') {
            const updatedServers = configStore.servers.map(n => {
                if (n.type === server.type) {
                    const updatedEndpoints = n.endpoints.map(ep =>
                        ep.description === server.selectedEndpoint.description ? endpoint : ep
                    );
                    const updatedSelectedEndpoint = endpoint;
                    return {
                        ...n,
                        endpoints: updatedEndpoints,
                        selectedEndpoint: updatedSelectedEndpoint,
                    };
                }
                return n;
            });

            configStore.setServers(updatedServers);
        }
    };

    const handleRemoveEndpoint = (server: Server, endpoint: Endpoint) => {
        const updatedServers = configStore.servers.map(s => {
            if (s.type === server.type) {
                const updatedEndpoints = s.endpoints.filter(ep => ep.description !== endpoint.description);
                const isRemovedEndpointSelected = s.selectedEndpoint.description === endpoint.description;
                return {
                    ...s,
                    endpoints: updatedEndpoints,
                    selectedEndpoint: isRemovedEndpointSelected ? (updatedEndpoints[0] || null) : s.selectedEndpoint,
                };
            }
            return s;
        });

        configStore.setServers(updatedServers);
        setDisplayConfirmationModal(false);
    };

    return (
        <View>
            <AddServerEndpointModal
                server={selectedServer}
                operation={selectedOperation}
                visible={displayEndpointModel}
                onClose={() => setDisplayEndpointModel(false)}
                onSubmit={(endpoint) => handleOnSubmit(selectedServer, endpoint)}
            />

            <ConfirmationModal
                visible={displayConfirmationModal}
                message="Are you sure you want to delete this endpoint?"
                onCancel={() => setDisplayConfirmationModal(false)}
                onConfirm={() => handleRemoveEndpoint(selectedServer, selectedEndpoint)}
            />
            <View style={styles.column}>
                {configStore.servers.map((server, index) => (
                    <View key={server.type} style={styles.row}>
                        <View>
                            <Text style={styles.label}>{server.name}</Text>
                        </View>
                        <TouchableOpacity
                            style={[IconStyles.container, ControlStyles.primary]}
                            onPress={() => {
                                setDisplayEndpointModel(true);
                                setSelectedOperation('add');
                                setSelectedServer(server);
                            }}
                        >
                            <Icon name="plus-circle" style={IconStyles.icon} />
                        </TouchableOpacity>
                        <View style={styles.pickerWrapper}>
                            <Picker
                                key={index}
                                selectedValue={server.selectedEndpoint?.address}
                                onValueChange={(selectedValue) => handleEndpointChange(server, selectedValue)}
                                mode="dialog"
                                prompt="Select Endpoint"
                            >
                                {server.endpoints.map((endpoint, index) => (
                                    <Picker.Item
                                        key={index}
                                        label={`${endpoint.description} @ ${endpoint.address}:${endpoint.port}`}
                                        value={endpoint.address}
                                    />
                                ))}
                            </Picker>
                        </View>
                        <TouchableOpacity
                            style={[IconStyles.container, ControlStyles.primary]}
                            onPress={() => {
                                setDisplayEndpointModel(true);
                                setSelectedOperation('edit');
                                setSelectedServer(server);
                                setSelectedEndpoint(server.selectedEndpoint)
                            }}
                        >
                            <Icon name="edit" style={IconStyles.icon} />
                        </TouchableOpacity>
                        <TouchableOpacity
                            style={[IconStyles.container, ControlStyles.primary]}
                            onPress={() => {
                                setDisplayConfirmationModal(true)
                                setSelectedServer(server);
                                setSelectedEndpoint(server.selectedEndpoint);
                            }}
                        >
                            <Icon name="trash" style={IconStyles.icon} />
                        </TouchableOpacity>
                    </View>
                ))}
            </View>
        </View>
    )
}

const styles = StyleSheet.create({
    column: {
        flexDirection: 'column',
    },
    row: {
        flexDirection: 'row',
        alignItems: 'center',
        paddingHorizontal: 5,
        marginVertical: 5,
        marginHorizontal: 0,
        backgroundColor: '#999',
        borderRadius: 5
    },
    header: {
        fontSize: 20,
        fontWeight: "bold",
        textAlign: 'center'
    },
    pickerWrapper: {
        flex: 1,
        borderColor: "#ccc",
        borderWidth: 1,
        marginHorizontal: 5,
    },
    buttonsWrapper: {
        flexShrink: 1,
        flexDirection: 'row',
        alignItems: 'center',
        borderColor: "#ccc",
        borderWidth: 1,
        marginHorizontal: 5,
    },
    label: {
        fontWeight: 'bold',
        marginBottom: 5,
        width: 100,
        fontSize: 16     
    },
});

