import { useEffect, useState, useRef, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';
import { QuadData } from '@/src/interfaces/messages';
import { useEndpointByType } from './config/useConfigStore';
import { ServerType } from '@/services/config/configTypes';

export function useDataTransfer(): {
  quadData: QuadData | undefined;
  connected: boolean;
  sendMessage: (msg: string) => void;
} {
  const [quadData, setQuadData] = useState<QuadData>();
  const [connected, setConnected] = useState(false);
  const socketRef = useRef<Socket | null>(null);
  const endpointByType = useEndpointByType(ServerType.QUADRUPED)

  const lastDataTimestamp = useRef(0);
  const updateTimestamp = useRef(0);

  const noDataTimeoutMs = 1000;

useEffect(() => {
  const interval = setInterval(() => {
   

    if (quadData?.timestamp) {
      if (lastDataTimestamp.current !== quadData.timestamp) {
        lastDataTimestamp.current = quadData.timestamp;
        updateTimestamp.current = Date.now();
        console.log(updateTimestamp.current);
      }
    }

    if (Date.now() - updateTimestamp.current > noDataTimeoutMs) {
      setConnected(false);
      setQuadData(undefined);
    } else {
       setConnected(true);
    }
    
  }, 25);

  return () => clearInterval(interval);
}, [quadData, noDataTimeoutMs]);


  useEffect(() => {
    if (endpointByType) {
      console.log(`[Data Transfer] using socket ${endpointByType?.description} @ ${endpointByType?.address}`);
      socketRef.current = io(endpointByType?.address);

      socketRef.current.on('connect', () => {
        console.log('[Data Transfer] connected to Socket.IO server');       
      });

      socketRef.current.on('message', (message: string) => {        
        setQuadData(JSON.parse(message));
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

  return { quadData: quadData, connected, sendMessage };
}
