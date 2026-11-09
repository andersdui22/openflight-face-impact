import { beforeEach, describe, expect, it, vi } from 'vitest';

type Ack = (error: Error | null, response?: unknown) => void;
const transport = vi.hoisted(() => {
  const listeners = new Map<string, (...args: unknown[]) => void>();
  const socket = {
    connected: false,
    close: vi.fn(),
    emit: vi.fn(),
    timeout: vi.fn(),
    on: vi.fn((name: string, callback: (...args: unknown[]) => void) => {
      listeners.set(name, callback);
    }),
  };
  socket.timeout.mockReturnValue(socket);
  return { socket, listeners, io: vi.fn(() => socket) };
});

vi.mock('socket.io-client', () => ({ io: transport.io }));
import { socketService } from './socketService';

const validResult = {
  schema_version: 1,
  source: 'synthetic_python_pipeline',
  ok: true,
  case_id: 'toe-high',
  label: 'Toe / high',
  polygon_face_mm: [
    [-50, -25],
    [50, -25],
    [40, 25],
  ],
  result: {
    status: 'ok',
    x_mm: 12,
    y_mm: 5,
    horizontal_region: 'toe',
    vertical_region: 'high',
  },
};

describe('synthetic Socket.IO client integration (mock transport)', () => {
  beforeEach(() => {
    socketService.disconnect();
    transport.listeners.clear();
    transport.socket.connected = false;
    vi.clearAllMocks();
    transport.socket.timeout.mockReturnValue(transport.socket);
  });

  it('does not send a request while disconnected', async () => {
    await expect(socketService.requestSyntheticFaceImpact('toe-high')).rejects.toThrow('disconnected');
    expect(transport.socket.emit).not.toHaveBeenCalled();
  });

  it('reuses the existing connection and handles backend acknowledgement', async () => {
    socketService.connect();
    transport.socket.connected = true;
    transport.listeners.get('connect')?.();
    const pending = socketService.requestSyntheticFaceImpact('toe-high');
    expect(transport.io).toHaveBeenCalledTimes(1);
    expect(transport.socket.timeout).toHaveBeenCalledWith(5000);
    const call = transport.socket.emit.mock.calls.find(([event]) => event === 'get_synthetic_face_impact');
    expect(call?.[1]).toEqual({ case_id: 'toe-high' });
    (call?.[2] as Ack)(null, validResult);
    await expect(pending).resolves.toMatchObject({ ok: true, case_id: 'toe-high' });
    socketService.connect();
    expect(transport.io).toHaveBeenCalledTimes(1);
  });

  it('rejects invalid, mismatched and timed-out backend acknowledgements', async () => {
    socketService.connect();
    transport.socket.connected = true;
    for (const response of [
      { ...validResult, case_id: 'heel-low' },
      { ...validResult, result: { status: 'ok' } },
    ]) {
      const pending = socketService.requestSyntheticFaceImpact('toe-high');
      const call = transport.socket.emit.mock.calls.at(-1);
      (call?.[2] as Ack)(null, response);
      await expect(pending).rejects.toThrow();
    }
    const pending = socketService.requestSyntheticFaceImpact('toe-high');
    const call = transport.socket.emit.mock.calls.at(-1);
    (call?.[2] as Ack)(new Error('timeout'));
    await expect(pending).rejects.toThrow('unavailable');
  });

  it('rejects disconnected requests then reconnects without a duplicate live socket', async () => {
    socketService.connect();
    transport.socket.connected = true;
    transport.listeners.get('connect')?.();
    transport.socket.connected = false;
    transport.listeners.get('disconnect')?.();
    await expect(socketService.requestSyntheticFaceImpact('toe-high')).rejects.toThrow('disconnected');
    transport.socket.connected = true;
    transport.listeners.get('connect')?.();
    const pending = socketService.requestSyntheticFaceImpact('toe-high');
    const call = transport.socket.emit.mock.calls.at(-1);
    (call?.[2] as Ack)(null, validResult);
    await expect(pending).resolves.toMatchObject({ ok: true });
    expect(transport.io).toHaveBeenCalledTimes(1);
  });
});
