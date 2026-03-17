import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// eslint-disable-next-line @typescript-eslint/no-require-imports
const { shouldUpdateScroll } = require('../../gatsby-browser');

describe('shouldUpdateScroll', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('returns true when there is no hash', () => {
    const result = shouldUpdateScroll({
      routerProps: { location: { hash: '' } },
    });
    expect(result).toBe(true);
  });

  it('returns false and scrolls to element when hash is present', () => {
    const mockElement = document.createElement('div');
    mockElement.id = 'about';
    document.body.appendChild(mockElement);

    const result = shouldUpdateScroll({
      routerProps: { location: { hash: '#about' } },
    });

    expect(result).toBe(false);

    vi.advanceTimersByTime(800);

    expect(mockElement.scrollIntoView).toHaveBeenCalledWith({
      behavior: 'smooth',
      block: 'start',
    });

    document.body.removeChild(mockElement);
  });

  it('does not throw when hash element does not exist', () => {
    const result = shouldUpdateScroll({
      routerProps: { location: { hash: '#nonexistent' } },
    });

    expect(result).toBe(false);

    expect(() => vi.advanceTimersByTime(800)).not.toThrow();
  });
});
