import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import useScrollDirection from './useScrollDirection';

describe('useScrollDirection', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    Object.defineProperty(window, 'pageYOffset', {
      writable: true,
      value: 0,
    });
  });

  it('should return down initially by default', () => {
    const { result } = renderHook(() => useScrollDirection());
    expect(result.current).toBe('down');
  });

  it('should return custom initial direction', () => {
    const { result } = renderHook(() =>
      useScrollDirection({ initialDirection: 'up' })
    );
    expect(result.current).toBe('up');
  });

  it('should return down when scrolling down', async () => {
    const { result } = renderHook(() => useScrollDirection());

    // Simulate scroll down
    Object.defineProperty(window, 'pageYOffset', {
      writable: true,
      value: 100,
    });

    window.dispatchEvent(new Event('scroll'));

    await waitFor(() => {
      expect(result.current).toBe('down');
    });
  });

  it('should return up when scrolling up', async () => {
    // Start at scrolled position
    Object.defineProperty(window, 'pageYOffset', {
      writable: true,
      value: 100,
    });

    const { result } = renderHook(() => useScrollDirection());

    // Simulate scroll up
    Object.defineProperty(window, 'pageYOffset', {
      writable: true,
      value: 50,
    });

    window.dispatchEvent(new Event('scroll'));

    await waitFor(() => {
      expect(result.current).toBe('up');
    });
  });

  it('should respect scroll threshold', async () => {
    const { result } = renderHook(() =>
      useScrollDirection({ thresholdPixels: 50 })
    );

    // Scroll less than threshold
    Object.defineProperty(window, 'pageYOffset', {
      writable: true,
      value: 30,
    });

    window.dispatchEvent(new Event('scroll'));

    // Should not change direction
    await new Promise(resolve => setTimeout(resolve, 100));
    expect(result.current).toBe('down');

    // Scroll more than threshold
    Object.defineProperty(window, 'pageYOffset', {
      writable: true,
      value: 100,
    });

    window.dispatchEvent(new Event('scroll'));

    await waitFor(() => {
      expect(result.current).toBe('down');
    });
  });

  it('should not add event listener when off is true', () => {
    const addEventListenerSpy = vi.spyOn(window, 'addEventListener');

    renderHook(() => useScrollDirection({ off: true }));

    expect(addEventListenerSpy).not.toHaveBeenCalledWith('scroll', expect.any(Function));
  });

  it('should return initial direction when off is true', () => {
    const { result } = renderHook(() =>
      useScrollDirection({ off: true, initialDirection: 'up' })
    );

    expect(result.current).toBe('up');
  });

  it('should throttle scroll events with requestAnimationFrame', async () => {
    const rafSpy = vi.spyOn(window, 'requestAnimationFrame');

    renderHook(() => useScrollDirection());

    // Trigger multiple scroll events
    window.dispatchEvent(new Event('scroll'));
    window.dispatchEvent(new Event('scroll'));
    window.dispatchEvent(new Event('scroll'));

    await waitFor(() => {
      expect(rafSpy).toHaveBeenCalledTimes(1);
    });
  });

  it('should clean up event listener on unmount', () => {
    const removeEventListenerSpy = vi.spyOn(window, 'removeEventListener');

    const { unmount } = renderHook(() => useScrollDirection());
    unmount();

    expect(removeEventListenerSpy).toHaveBeenCalledWith('scroll', expect.any(Function));
  });

  it('should handle scroll position of 0', async () => {
    Object.defineProperty(window, 'pageYOffset', {
      writable: true,
      value: 100,
    });

    const { result } = renderHook(() => useScrollDirection());

    // Scroll to top
    Object.defineProperty(window, 'pageYOffset', {
      writable: true,
      value: 0,
    });

    window.dispatchEvent(new Event('scroll'));

    await waitFor(() => {
      expect(result.current).toBe('up');
    });
  });
});
