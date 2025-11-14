import { describe, it, expect, vi, beforeEach } from 'vitest';
import { getSr } from './sr';

describe('getSr', () => {
  beforeEach(() => {
    // Reset the module to clear cached instance
    vi.resetModules();
  });

  it('should return null in SSR environment', async () => {
    const originalWindow = global.window;
    // @ts-expect-error - testing SSR
    delete global.window;

    const { getSr: getSrSSR } = await import('./sr');
    const result = await getSrSSR();

    expect(result).toBeNull();

    // Restore window
    global.window = originalWindow;
  });

  it('should lazy load scrollreveal library', async () => {
    const result = await getSr();
    expect(result).toBeDefined();
    expect(typeof result).toBe('object');
  });

  it('should return cached instance on subsequent calls', async () => {
    const firstCall = await getSr();
    const secondCall = await getSr();

    expect(firstCall).toBe(secondCall);
  });

  it('should have reveal method', async () => {
    const sr = await getSr();
    expect(sr.reveal).toBeDefined();
    expect(typeof sr.reveal).toBe('function');
  });

  it('should have sync method', async () => {
    const sr = await getSr();
    expect(sr.sync).toBeDefined();
    expect(typeof sr.sync).toBe('function');
  });

  it('should have clean method', async () => {
    const sr = await getSr();
    expect(sr.clean).toBeDefined();
    expect(typeof sr.clean).toBe('function');
  });
});
