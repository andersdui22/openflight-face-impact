import { useEffect, useCallback } from 'react';
import { socketService } from '../services/socketService';

export function useSocket() {
  useEffect(() => {
    socketService.connect();
  }, []);

  const shutdown = useCallback(async () => {
    if (window.openFlightDesktop) {
      window.openFlightDesktop.quit();
      return;
    }
    const response = await fetch('/api/shutdown', { method: 'POST' });
    if (!response.ok) {
      throw new Error(`Shutdown request failed (${response.status})`);
    }
  }, []);

  const sleepScreen = useCallback(async () => {
    const response = await fetch('/api/screen/sleep', { method: 'POST' });
    if (!response.ok) {
      throw new Error(`Screen sleep request failed (${response.status})`);
    }
  }, []);

  return { shutdown, sleepScreen };
}
