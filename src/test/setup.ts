import '@testing-library/jest-dom';
import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';
import React from 'react';

// Extend Vitest matchers with jest-dom
expect.extend(matchers);

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return [];
  }
  unobserve() {}
} as any;

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock scrollTo
window.scrollTo = vi.fn();

// Mock scrollIntoView
Element.prototype.scrollIntoView = vi.fn();

// Mock gatsby
vi.mock('gatsby', async () => {
  const actual = await vi.importActual('gatsby');
  return {
    ...actual,
    graphql: vi.fn(),
    Link: ({ to, children, ...props }: any) =>
      React.createElement('a', { href: to, ...props }, children),
    StaticQuery: vi.fn(),
    useStaticQuery: vi.fn(),
  };
});

// Mock gatsby-plugin-image
vi.mock('gatsby-plugin-image', () => ({
  GatsbyImage: ({ image, alt }: any) =>
    React.createElement('img', { src: image?.src, alt }),
  StaticImage: ({ src, alt }: any) => React.createElement('img', { src, alt }),
  getImage: (image: any) => image,
}));

// Mock scrollreveal
vi.mock('scrollreveal', () => ({
  default: vi.fn(() => ({
    reveal: vi.fn(),
    sync: vi.fn(),
    clean: vi.fn(),
  })),
}));

// Mock animejs
vi.mock('animejs', () => ({
  default: vi.fn(() => ({
    play: vi.fn(),
    pause: vi.fn(),
    restart: vi.fn(),
  })),
}));
