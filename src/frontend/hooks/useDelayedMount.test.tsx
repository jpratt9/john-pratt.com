import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import useDelayedMount from './useDelayedMount';
import * as usePrefersReducedMotionModule from './usePrefersReducedMotion';

vi.mock('./usePrefersReducedMotion');

describe('useDelayedMount', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(usePrefersReducedMotionModule, 'default').mockReturnValue(false);
  });

  it('should return false initially', () => {
    const { result } = renderHook(() => useDelayedMount(1000));
    expect(result.current).toBe(false);
  });

  it('should return true after delay', async () => {
    const { result } = renderHook(() => useDelayedMount(100));

    expect(result.current).toBe(false);

    await waitFor(() => {
      expect(result.current).toBe(true);
    }, { timeout: 200 });
  });

  it('should use custom delay when provided', async () => {
    const { result } = renderHook(() => useDelayedMount(150));

    expect(result.current).toBe(false);

    await waitFor(() => {
      expect(result.current).toBe(true);
    }, { timeout: 300 });
  });

  it('should clean up timeout on unmount', () => {
    const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout');
    const { unmount } = renderHook(() => useDelayedMount(1000));

    unmount();

    expect(clearTimeoutSpy).toHaveBeenCalled();
  });

  it('should handle zero delay', async () => {
    const { result } = renderHook(() => useDelayedMount(0));

    await waitFor(() => {
      expect(result.current).toBe(true);
    }, { timeout: 100 });
  });

  it('should return true immediately with reduced motion preference', () => {
    vi.spyOn(usePrefersReducedMotionModule, 'default').mockReturnValue(true);

    const { result } = renderHook(() => useDelayedMount(1000));
    expect(result.current).toBe(true);
  });

  it('should return true immediately when condition is false', () => {
    const { result } = renderHook(() => useDelayedMount(1000, false));
    expect(result.current).toBe(true);
  });

  it('should not start timer when condition is false', () => {
    const setTimeoutSpy = vi.spyOn(global, 'setTimeout');
    renderHook(() => useDelayedMount(1000, false));

    expect(setTimeoutSpy).not.toHaveBeenCalled();
  });

  it('should not start timer with reduced motion', () => {
    vi.spyOn(usePrefersReducedMotionModule, 'default').mockReturnValue(true);
    const setTimeoutSpy = vi.spyOn(global, 'setTimeout');

    renderHook(() => useDelayedMount(1000));

    expect(setTimeoutSpy).not.toHaveBeenCalled();
  });
});
