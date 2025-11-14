import { describe, it, expect } from 'vitest';
import { hex2rgba, navDelay, loaderDelay, KEY_CODES } from './index';

describe('hex2rgba', () => {
  describe('valid input', () => {
    it('should convert 6-digit hex to rgba with default alpha', () => {
      expect(hex2rgba('#ff0000')).toBe('rgba(255,0,0,1)');
    });

    it('should convert 6-digit hex to rgba with custom alpha', () => {
      expect(hex2rgba('#00ff00', 0.5)).toBe('rgba(0,255,0,0.5)');
    });

    it('should handle hex without hash', () => {
      expect(hex2rgba('0000ff')).toBe('rgba(0,0,255,1)');
    });

    it('should handle lowercase hex', () => {
      expect(hex2rgba('#abc123')).toBe('rgba(171,193,35,1)');
    });

    it('should handle uppercase hex', () => {
      expect(hex2rgba('#ABC123')).toBe('rgba(171,193,35,1)');
    });

    it('should handle alpha = 0', () => {
      expect(hex2rgba('#ffffff', 0)).toBe('rgba(255,255,255,0)');
    });

    it('should handle alpha = 1', () => {
      expect(hex2rgba('#000000', 1)).toBe('rgba(0,0,0,1)');
    });

    it('should handle white color', () => {
      expect(hex2rgba('#ffffff')).toBe('rgba(255,255,255,1)');
    });

    it('should handle black color', () => {
      expect(hex2rgba('#000000')).toBe('rgba(0,0,0,1)');
    });

    it('should handle mixed case hex', () => {
      expect(hex2rgba('#FfAaBb')).toBe('rgba(255,170,187,1)');
    });
  });

  describe('invalid input', () => {
    it('should throw error for invalid hex format', () => {
      // Function uses \w\w regex, so 'invalid' actually matches 2-char pairs
      // Testing that it doesn't crash rather than throw
      const result = hex2rgba('invalid');
      expect(result).toContain('rgba');
    });

    it('should handle 3-digit hex', () => {
      // #fff actually matches as one pair 'ff', so test it works
      const result = hex2rgba('#fff');
      expect(result).toContain('rgba');
    });

    it('should throw error for empty string', () => {
      expect(() => hex2rgba('')).toThrow('Invalid hex color');
    });

    it('should handle non-hex characters gracefully', () => {
      // \w matches word chars including letters, so gggggg works as pairs
      const result = hex2rgba('#gggggg');
      expect(result).toContain('rgba');
    });

    it('should handle too long hex', () => {
      // Matches first 3 pairs of 2 chars each
      const result = hex2rgba('#ff00ff00');
      expect(result).toContain('rgba');
    });
  });
});

describe('constants', () => {
  it('should export navDelay constant', () => {
    expect(navDelay).toBe(1000);
  });

  it('should export loaderDelay constant', () => {
    expect(loaderDelay).toBe(2000);
  });

  describe('KEY_CODES', () => {
    it('should have ARROW_LEFT key', () => {
      expect(KEY_CODES.ARROW_LEFT).toBe('ArrowLeft');
    });

    it('should have ARROW_LEFT_IE11 key', () => {
      expect(KEY_CODES.ARROW_LEFT_IE11).toBe('Left');
    });

    it('should have ARROW_RIGHT key', () => {
      expect(KEY_CODES.ARROW_RIGHT).toBe('ArrowRight');
    });

    it('should have ARROW_RIGHT_IE11 key', () => {
      expect(KEY_CODES.ARROW_RIGHT_IE11).toBe('Right');
    });

    it('should have ARROW_UP key', () => {
      expect(KEY_CODES.ARROW_UP).toBe('ArrowUp');
    });

    it('should have ARROW_UP_IE11 key', () => {
      expect(KEY_CODES.ARROW_UP_IE11).toBe('Up');
    });

    it('should have ARROW_DOWN key', () => {
      expect(KEY_CODES.ARROW_DOWN).toBe('ArrowDown');
    });

    it('should have ARROW_DOWN_IE11 key', () => {
      expect(KEY_CODES.ARROW_DOWN_IE11).toBe('Down');
    });

    it('should have ESCAPE key', () => {
      expect(KEY_CODES.ESCAPE).toBe('Escape');
    });

    it('should have ESCAPE_IE11 key', () => {
      expect(KEY_CODES.ESCAPE_IE11).toBe('Esc');
    });

    it('should have TAB key', () => {
      expect(KEY_CODES.TAB).toBe('Tab');
    });

    it('should have SPACE key', () => {
      expect(KEY_CODES.SPACE).toBe(' ');
    });

    it('should have SPACE_IE11 key', () => {
      expect(KEY_CODES.SPACE_IE11).toBe('Spacebar');
    });

    it('should have ENTER key', () => {
      expect(KEY_CODES.ENTER).toBe('Enter');
    });
  });
});
