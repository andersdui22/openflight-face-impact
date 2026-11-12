export {};

declare global {
  interface Window {
    openFlightDesktop?: {
      quit: () => void;
      backendAvailable: boolean;
    };
  }
}
