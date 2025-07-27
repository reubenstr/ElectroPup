import { Server, ServerType } from "./configTypes";

export const defaultServers: Server[] = [
    {
        type: ServerType.HEXAPOD,
        name: "Hexapod",
        endpoints: [
            { description: "Local WiFi", address: "192.168.1.143", port: 80, encrypted: false },
            { description: "Hexapod's WiFi", address: "192.168.1.101", port: 80, encrypted: false }],
        selectedEndpoint: { description: "Local WiFi", address: "192.168.1.143", port: 80, encrypted: false}
    },
];

