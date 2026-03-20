import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// eslint-disable-next-line @typescript-eslint/no-require-imports
const { onRouteUpdate, shouldUpdateScroll } = require('../../gatsby-browser');

describe('gatsby-browser', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('shouldUpdateScroll', () => {
    it('returns true when there is no hash', () => {
      const result = shouldUpdateScroll({
        routerProps: { location: { hash: '' } },
      });
      expect(result).toBe(true);
    });

    it('returns false when hash is present', () => {
      const result = shouldUpdateScroll({
        routerProps: { location: { hash: '#about' } },
      });
      expect(result).toBe(false);
    });
  });

  describe('onRouteUpdate', () => {
    it('scrolls to element when hash is present and element exists', () => {
      const mockElement = document.createElement('div');
      mockElement.id = 'about';
      document.body.appendChild(mockElement);

      const scrollToSpy = vi.spyOn(window, 'scrollTo').mockImplementation(() => {});

      onRouteUpdate({ location: { hash: '#about' } });

      vi.advanceTimersByTime(200);

      expect(scrollToSpy).toHaveBeenCalled();

      scrollToSpy.mockRestore();
      document.body.removeChild(mockElement);
    });

    it('does not throw when hash element does not exist', () => {
      onRouteUpdate({ location: { hash: '#nonexistent' } });
      expect(() => vi.advanceTimersByTime(200)).not.toThrow();
    });

    it('does nothing when there is no hash', () => {
      expect(() => onRouteUpdate({ location: { hash: '' } })).not.toThrow();
    });
  });
});
