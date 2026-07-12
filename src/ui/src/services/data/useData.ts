import { useEffect } from "react";
import { io, Socket } from "socket.io-client";
import { Data } from "@/services/data/dataTypes";
import { useDataStore } from "@/services/data/useDataStore";
import { useConfigStore } from "@/services/config/useConfigStore";
import { generateUrl, selectedEndpoint } from "@/services/config/configUtilities";

const NO_DATA_TIMEOUT_MS = 1000;

let socket: Socket | null = null;

export function sendMessage(message: string) {
    if (!socket?.connected) {
        console.warn("[Data] cannot send, socket not connected");
        return;
    }
    socket.emit("message", message);
}

export function useData() {
    const endpoint = useConfigStore((state) => selectedEndpoint(state.config));

    const setData = useDataStore((state) => state.setData);
    const clearData = useDataStore((state) => state.clearData);
    const setStatus = useDataStore((state) => state.setStatus);

    useEffect(() => {
        if (!endpoint) {
            setStatus("disconnected");
            return;
        }

        const url = generateUrl(endpoint);
        console.log(`[data] connecting to ${endpoint.description} @ ${url}`);

        setStatus("connecting");
        const connection = io(url);
        socket = connection;

        let staleTimer: ReturnType<typeof setTimeout> | undefined;

        connection.on("connect", () => setStatus("connected"));
        connection.on("disconnect", () => setStatus("disconnected"));

        connection.on("message", (message: string) => {
            try {
                setData(JSON.parse(message) as Data);
            } catch {
                console.warn("[Data] discarding unparseable message");
                return;
            }
            clearTimeout(staleTimer);
            staleTimer = setTimeout(clearData, NO_DATA_TIMEOUT_MS);
        });

        const onReconnectAttempt = () => setStatus("connecting");
        connection.io.on("reconnect_attempt", onReconnectAttempt);

        return () => {
            clearTimeout(staleTimer);
            connection.io.off("reconnect_attempt", onReconnectAttempt);
            connection.off();
            connection.disconnect();
            socket = null;
            setStatus("disconnected");
        };
    }, [endpoint, setData, clearData, setStatus]);
}

export default useData;
