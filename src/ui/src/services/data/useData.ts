import { useEffect, useState, useRef, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import { Data } from '@/services/data/dataTypes';


export function useData(): {
    data: Data | undefined;
    connected: boolean;
    sendMessage: (msg: string) => void;
} {
    const [data, setData] = useState<Data>();
    const [connected, setConnected] = useState(false);
    const socketRef = useRef<Socket | null>(null);
    const endpointByType = // get endpoitn from the store

  const lastDataTimestamp = useRef(0);
    const updateTimestamp = useRef(0);

    const noDataTimeoutMs = 1000;

    useEffect(() => {
        const interval = setInterval(() => {


            if (data?.timestamp) {
                if (lastDataTimestamp.current !== data.timestamp) {
                    lastDataTimestamp.current = data.timestamp;
                    updateTimestamp.current = Date.now();
                    console.log(updateTimestamp.current);
                }
            }

            if (Date.now() - updateTimestamp.current > noDataTimeoutMs) {
                setConnected(false);
                setData(undefined);
            } else {
                setConnected(true);
            }

        }, 25);

        return () => clearInterval(interval);
    }, [data, noDataTimeoutMs]);


    useEffect(() => {
        if (endpointByType) {
            console.log(`[Data Transfer] using socket ${endpointByType?.description} @ ${endpointByType?.address}`);
            socketRef.current = io(endpointByType?.address);

            socketRef.current.on('connect', () => {
                console.log('[Data Transfer] connected to Socket.IO server');
            });

            socketRef.current.on('message', (message: string) => {
                setData(JSON.parse(message));
            });

            socketRef.current.on('disconnect', () => {
                console.log('[Data Transfer] disconnected from Socket.IO server');
            });
        }
        return () => {
            socketRef.current?.disconnect();
        };
    }, [endpointByType]);

    const sendMessage = useCallback((msg: string) => {
        if (socketRef.current?.connected) {
            socketRef.current.emit('message', msg);
        } else {
            console.warn('[Data Transfer] cannot send, socket not connected');
        }
    }, []);

    return { data, connected, sendMessage };
}
