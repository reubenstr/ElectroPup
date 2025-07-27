import { useEffect, useState, useRef, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import { QuadData } from '@/interfaces/messages';
import { useEndpointByType } from './config/useConfigStore';
import { ServerType } from '@/services/config/configTypes';

export function useDataTransfer(): {
  hexData: QuadData | undefined;
  connected: boolean;
  sendMessage: (msg: string) => void;
} {
  const [hexData, setHexData] = useState<QuadData>();
  const [connected, setConnected] = useState(false);
  const socketRef = useRef<Socket | null>(null);
  const endpointByType = useEndpointByType(ServerType.HEXAPOD)

  const noDataTimeoutMs = 3000;

  useEffect(() => {
    const interval = setInterval(() => {
     
      if (hexData && hexData?.timestamp) {
        if (Date.now() - hexData?.timestamp > noDataTimeoutMs) {
          setConnected(false)
          setHexData(undefined)
        }
      }
    }, 100);   
    return () => clearInterval(interval);
  }, [hexData]); 


  useEffect(() => {
    if (endpointByType) {
      console.log(`[DATA TRANSFER] using socket ${endpointByType?.description} @ ${endpointByType?.address}`);
      socketRef.current = io(endpointByType?.address);

      socketRef.current.on('connect', () => {
        console.log('[DATA TRANSFER] connected to Socket.IO server');
        setConnected(true);
      });

      socketRef.current.on('message', (message: string) => {
        // console.log('[DATA TRANSFER] message received:', message);
        // TODO: Check if message type is hexData        
        setHexData(JSON.parse(message));
      });

      socketRef.current.on('disconnect', () => {
        console.log('[DATA TRANSFER] disconnected from Socket.IO server');
        setConnected(false);
        setHexData(undefined)
      });
    }
    return () => {
      socketRef.current?.disconnect();
    };
  }, [endpointByType]);

  const sendMessage = useCallback((msg: string) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit('message', msg);
      // console.log('[DATA TRANSFER] Sent:', msg);
    } else {
      console.warn('[DATA TRANSFER] cannot send, socket not connected');
    }
  }, []);

  return { hexData, connected, sendMessage };
}
