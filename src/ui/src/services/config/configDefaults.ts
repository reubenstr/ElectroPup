import { Server, ServerType } from "./configTypes";

export const defaultServers: Server[] = [
    {
        type: ServerType.QUADRUPED,
        name: "Quadruped",
        endpoints: [
            { description: "Local WiFi", address: "192.168.1.144", port: 80, encrypted: false },
            { description: "Quadrupeds WiFi", address: "192.168.1.101", port: 80, encrypted: false }],
        selectedEndpoint: { description: "Local WiFi", address: "192.168.1.144", port: 80, encrypted: false}
    },
];

