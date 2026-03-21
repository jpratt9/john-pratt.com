import { describe, it, expect } from 'vitest';

// eslint-disable-next-line @typescript-eslint/no-require-imports
const gatsbyBrowser = require('../../gatsby-browser');

describe('gatsby-browser', () => {
  it('exports no browser APIs (scroll handled by layout)', () => {
    expect(Object.keys(gatsbyBrowser)).toEqual([]);
  });
});
