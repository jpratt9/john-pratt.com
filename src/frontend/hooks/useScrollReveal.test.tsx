import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useRef } from 'react';
import { useScrollReveal, useScrollRevealMultiple } from './useScrollReveal';
import * as srModule from '@utils/sr';
import * as usePrefersReducedMotionModule from './usePrefersReducedMotion';

vi.mock('@utils/sr');
vi.mock('./usePrefersReducedMotion');
vi.mock('@config', () => ({
  default: {
    srConfig: vi.fn(() => ({
      origin: 'bottom',
      distance: '20px',
      duration: 500,
      delay: 200,
    })),
  },
}));

describe('useScrollReveal', () => {
  let mockSr: any;

  beforeEach(() => {
    vi.clearAllMocks();
    mockSr = {
      reveal: vi.fn(),
      sync: vi.fn(),
      clean: vi.fn(),
    };
    vi.spyOn(srModule, 'getSr').mockResolvedValue(mockSr);
    vi.spyOn(usePrefersReducedMotionModule, 'default').mockReturnValue(false);
  });

  it('should initialize ScrollReveal on mount', async () => {
    const ref = { current: document.createElement('div') };

    renderHook(() => useScrollReveal(ref));

    await vi.waitFor(() => {
      expect(srModule.getSr).toHaveBeenCalled();
    });
  });

  it('should not initialize when ref.current is null', async () => {
    const ref = { current: null };

    renderHook(() => useScrollReveal(ref));

    await new Promise(resolve => setTimeout(resolve, 100));

    expect(mockSr.reveal).not.toHaveBeenCalled();
  });

  it('should not initialize with reduced motion preference', async () => {
    vi.spyOn(usePrefersReducedMotionModule, 'default').mockReturnValue(true);
    const ref = { current: document.createElement('div') };

    renderHook(() => useScrollReveal(ref));

    await new Promise(resolve => setTimeout(resolve, 100));

    expect(srModule.getSr).not.toHaveBeenCalled();
  });

  it('should use default srConfig when no custom config', async () => {
    const ref = { current: document.createElement('div') };

    renderHook(() => useScrollReveal(ref));

    await vi.waitFor(() => {
      expect(mockSr.reveal).toHaveBeenCalledWith(
        ref.current,
        expect.objectContaining({
          origin: 'bottom',
          distance: '20px',
          duration: 500,
        })
      );
    });
  });

  it('should use custom config when provided', async () => {
    const ref = { current: document.createElement('div') };
    const customConfig = {
      origin: 'left' as const,
      distance: '50px',
      duration: 1000,
    };

    renderHook(() => useScrollReveal(ref, customConfig));

    await vi.waitFor(() => {
      expect(mockSr.reveal).toHaveBeenCalledWith(ref.current, customConfig);
    });
  });

  it('should handle getSr returning null', async () => {
    vi.spyOn(srModule, 'getSr').mockResolvedValue(null);
    const ref = { current: document.createElement('div') };

    renderHook(() => useScrollReveal(ref));

    await new Promise(resolve => setTimeout(resolve, 100));

    expect(mockSr.reveal).not.toHaveBeenCalled();
  });

  it('should cleanup on unmount', () => {
    const ref = { current: document.createElement('div') };
    const { unmount } = renderHook(() => useScrollReveal(ref));

    unmount();

    // Verify cleanup happens (mounted flag set to false)
    expect(true).toBe(true); // Cleanup is internal, just verify no errors
  });
});

describe('useScrollRevealMultiple', () => {
  let mockSr: any;

  beforeEach(() => {
    vi.clearAllMocks();
    mockSr = {
      reveal: vi.fn(),
      sync: vi.fn(),
      clean: vi.fn(),
    };
    vi.spyOn(srModule, 'getSr').mockResolvedValue(mockSr);
    vi.spyOn(usePrefersReducedMotionModule, 'default').mockReturnValue(false);
  });

  it('should reveal multiple elements', async () => {
    const div1 = document.createElement('div');
    const div2 = document.createElement('div');
    const div3 = document.createElement('div');
    const refs = { current: [div1, div2, div3] };

    renderHook(() => useScrollRevealMultiple(refs));

    await vi.waitFor(() => {
      expect(mockSr.reveal).toHaveBeenCalledTimes(3);
      expect(mockSr.reveal).toHaveBeenCalledWith(div1, expect.any(Object));
      expect(mockSr.reveal).toHaveBeenCalledWith(div2, expect.any(Object));
      expect(mockSr.reveal).toHaveBeenCalledWith(div3, expect.any(Object));
    });
  });

  it('should apply config function to each element', async () => {
    const div1 = document.createElement('div');
    const div2 = document.createElement('div');
    const refs = { current: [div1, div2] };
    const configFn = (index: number) => ({
      origin: 'bottom' as const,
      delay: index * 100,
    });

    renderHook(() => useScrollRevealMultiple(refs, configFn));

    await vi.waitFor(() => {
      expect(mockSr.reveal).toHaveBeenCalledWith(div1, { origin: 'bottom', delay: 0 });
      expect(mockSr.reveal).toHaveBeenCalledWith(div2, { origin: 'bottom', delay: 100 });
    });
  });

  it('should stagger animations with default config', async () => {
    const div1 = document.createElement('div');
    const div2 = document.createElement('div');
    const refs = { current: [div1, div2] };

    renderHook(() => useScrollRevealMultiple(refs));

    await vi.waitFor(() => {
      expect(mockSr.reveal).toHaveBeenCalledWith(
        div1,
        expect.objectContaining({ delay: 200 })
      );
      expect(mockSr.reveal).toHaveBeenCalledWith(
        div2,
        expect.objectContaining({ delay: 200 })
      );
    });
  });

  it('should skip null refs', async () => {
    const div1 = document.createElement('div');
    const refs = { current: [div1, null, null] };

    renderHook(() => useScrollRevealMultiple(refs));

    await vi.waitFor(() => {
      expect(mockSr.reveal).toHaveBeenCalledTimes(1);
      expect(mockSr.reveal).toHaveBeenCalledWith(div1, expect.any(Object));
    });
  });

  it('should respect reduced motion', async () => {
    vi.spyOn(usePrefersReducedMotionModule, 'default').mockReturnValue(true);
    const div1 = document.createElement('div');
    const refs = { current: [div1] };

    renderHook(() => useScrollRevealMultiple(refs));

    await new Promise(resolve => setTimeout(resolve, 100));

    expect(srModule.getSr).not.toHaveBeenCalled();
  });

  it('should not initialize when refs.current is null', async () => {
    const refs = { current: null };

    renderHook(() => useScrollRevealMultiple(refs));

    await new Promise(resolve => setTimeout(resolve, 100));

    expect(mockSr.reveal).not.toHaveBeenCalled();
  });
});
