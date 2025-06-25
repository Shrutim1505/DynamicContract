import { useState, useEffect } from "react";
import { useWebSocket } from "./use-websocket";
import { PresenceUser, CursorPosition } from "@/types/presence";

export function usePresence(userId: number, contractId: number) {
  const [activeUsers, setActiveUsers] = useState<PresenceUser[]>([]);
  const [cursors, setCursors] = useState<CursorPosition[]>([]);
  const { onMessage, sendMessage } = useWebSocket(userId, contractId);

  useEffect(() => {
    const cleanup1 = onMessage('presence_update', (data: any) => {
      if (data.action === 'joined') {
        setActiveUsers(prev => {
          const filtered = prev.filter(user => user.id !== data.userId);
          return [...filtered, {
            id: data.userId,
            fullName: data.user?.fullName || 'Unknown User',
            avatar: data.user?.avatar,
            position: data.position,
            isActive: true,
            lastSeen: new Date(),
          }];
        });
      } else if (data.action === 'left') {
        setActiveUsers(prev => prev.filter(user => user.id !== data.userId));
        setCursors(prev => prev.filter(cursor => cursor.userId !== data.userId));
      }
    });

    const cleanup2 = onMessage('cursor_update', (data: any) => {
      setCursors(prev => {
        const filtered = prev.filter(cursor => cursor.userId !== data.userId);
        return [...filtered, {
          userId: data.userId,
          position: data.position,
          user: {
            fullName: data.user?.fullName || 'Unknown User',
            avatar: data.user?.avatar,
          },
        }];
      });
    });

    return () => {
      cleanup1();
      cleanup2();
    };
  }, [onMessage]);

  const updateCursorPosition = (position: { line: number; character: number }) => {
    sendMessage({
      type: 'cursor_move',
      position,
    });
  };

  const sendContentChange = (content: string, wordCount: number) => {
    sendMessage({
      type: 'content_change',
      content,
      wordCount,
    });
  };

  return {
    activeUsers,
    cursors,
    updateCursorPosition,
    sendContentChange,
  };
}
