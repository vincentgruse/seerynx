import { useEffect, useState } from "react";

export type FeederStatus = "connecting" | "online" | "offline";

const RECONNECT_DELAY = 3000;

function getWebSocketUrl(): string {
  const apiUrl = new URL(import.meta.env.VITE_API_URL);
  const protocol = apiUrl.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${apiUrl.host}/api/devices/feeder/ws`;
}

export function useFeederStatus(): FeederStatus {
  const [status, setStatus] = useState<FeederStatus>("connecting");

  useEffect(() => {
    let socket: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    let cancelled = false;

    const connect = () => {
      socket = new WebSocket(getWebSocketUrl());

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as { online: boolean };
          setStatus(data.online ? "online" : "offline");
        } catch {
          // ignore malformed messages
        }
      };

      socket.onclose = () => {
        if (cancelled) return;
        setStatus("connecting");
        reconnectTimer = setTimeout(connect, RECONNECT_DELAY);
      };

      socket.onerror = () => {
        socket?.close();
      };
    };

    connect();

    return () => {
      cancelled = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      socket?.close();
    };
  }, []);

  return status;
}
