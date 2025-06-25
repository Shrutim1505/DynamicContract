import { useEffect, useRef } from "react";
import { wsManager } from "@/lib/websocket";

export function useWebSocket(userId: number, contractId: number) {
  const connectedRef = useRef(false);

  useEffect(() => {
    if (!connectedRef.current && userId && contractId) {
      wsManager.connect(userId, contractId);
      connectedRef.current = true;
    }

    return () => {
      if (connectedRef.current) {
        wsManager.disconnect();
        connectedRef.current = false;
      }
    };
  }, [userId, contractId]);

  const sendMessage = (message: any) => {
    wsManager.send(message);
  };

  const onMessage = (event: string, callback: Function) => {
    wsManager.on(event, callback);
    
    return () => {
      wsManager.off(event, callback);
    };
  };

  return {
    sendMessage,
    onMessage,
  };
}
