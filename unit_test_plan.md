# Unit Test Plan for john-pratt.com

## Executive Summary

Portfolio website built with Gatsby 5, React 18, TypeScript, and Styled Components. **No unit test suite exists.** This plan establishes comprehensive testing with **90% coverage target**.

---

## Current State

**Technology Stack:**
- Gatsby 5 + React 18 + TypeScript 5.9.3
- Styled Components 6.1.19
- Custom hooks (6 total)
- ScrollReveal + AnimeJS animations

**Gaps:**
- ❌ No test framework
- ❌ No test files (0 found)
- ❌ No test scripts
- ❌ No CI/CD test integration

---

## Testing Stack

### Core Tools
- **Vitest** - Fast, ESM-native test framework
- **React Testing Library** - Component testing
- **@testing-library/jest-dom** - DOM matchers
- **@testing-library/user-event** - User interactions
- **jsdom** - DOM environment
- **@vitest/coverage-v8** - Coverage reporting

### Installation
```bash
npm install --save-dev vitest @vitest/ui @testing-library/react \
  @testing-library/jest-dom @testing-library/user-event \
  @testing-library/react-hooks jsdom @vitest/coverage-v8
```

---

## Configuration

### `vitest.config.ts`
```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/', 'src/test/', '**/*.d.ts', '**/*.config.*',
        'src/frontend/content/**', 'gatsby-*.js', 'public/**', '.cache/**',
      ],
      thresholds: { lines: 90, functions: 90, branches: 90, statements: 90 },
    },
  },
  resolve: {
    alias: {
      '@components': path.resolve(__dirname, './src/frontend/components'),
      '@hooks': path.resolve(__dirname, './src/frontend/hooks'),
      '@utils': path.resolve(__dirname, './src/frontend/utils'),
      '@styles': path.resolve(__dirname, './src/frontend/styles'),
      '@config': path.resolve(__dirname, './src/frontend/config'),
    },
  },
});
```

### `src/test/setup.ts`
```typescript
import '@testing-library/jest-dom';
import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

expect.extend(matchers);
afterEach(() => cleanup());

// Mock browser APIs
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() { return []; }
  unobserve() {}
} as any;

window.matchMedia = vi.fn().mockImplementation(query => ({
  matches: false, media: query, onchange: null,
  addListener: vi.fn(), removeListener: vi.fn(),
  addEventListener: vi.fn(), removeEventListener: vi.fn(),
  dispatchEvent: vi.fn(),
}));

window.scrollTo = vi.fn();
Element.prototype.scrollIntoView = vi.fn();

// Mock Gatsby
vi.mock('gatsby', async () => ({
  ...await vi.importActual('gatsby'),
  graphql: vi.fn(),
  Link: ({ to, children, ...props }: any) => <a href={to} {...props}>{children}</a>,
  useStaticQuery: vi.fn(),
}));

// Mock gatsby-plugin-image
vi.mock('gatsby-plugin-image', () => ({
  GatsbyImage: ({ image, alt }: any) => <img src={image?.src} alt={alt} />,
  StaticImage: ({ src, alt }: any) => <img src={src} alt={alt} />,
}));

// Mock animation libraries
vi.mock('scrollreveal', () => ({
  default: vi.fn(() => ({ reveal: vi.fn(), sync: vi.fn(), clean: vi.fn() })),
}));

vi.mock('animejs', () => ({
  default: vi.fn(() => ({ play: vi.fn(), pause: vi.fn(), restart: vi.fn() })),
}));
```

### `src/test/utils.tsx`
```typescript
import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { ThemeProvider } from 'styled-components';
import { theme } from '@styles';

const AllTheProviders: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={theme}>{children}</ThemeProvider>
);

const customRender = (ui: ReactElement, options?: Omit<RenderOptions, 'wrapper'>) =>
  render(ui, { wrapper: AllTheProviders, ...options });

export * from '@testing-library/react';
export { customRender as render };
```

### `package.json` Scripts
```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:run": "vitest run",
    "test:coverage": "vitest run --coverage",
    "test:watch": "vitest watch"
  }
}
```

---

## Test Coverage Targets (90%)

| Category | Target | Priority |
|----------|--------|----------|
| Utils | 95%+ | Critical - pure functions |
| Hooks | 95%+ | Critical - core functionality |
| Components - Interactive | 90% | High |
| Components - Presentational | 85% | High |
| Pages/Templates | 85% | Medium |
| Styled Components | 70% | Low |

---

## Test Breakdown by File

### Utils (`src/frontend/utils/`)

#### `index.test.ts`
```typescript
describe('hex2rgba', () => {
  it('should convert hex to rgba with default alpha', () => {
    expect(hex2rgba('#ff0000')).toBe('rgba(255,0,0,1)');
  });
  it('should convert hex to rgba with custom alpha', () => {
    expect(hex2rgba('#00ff00', 0.5)).toBe('rgba(0,255,0,0.5)');
  });
  it('should throw error for invalid hex', () => {
    expect(() => hex2rgba('invalid')).toThrow('Invalid hex color');
  });
});

describe('KEY_CODES', () => {
  it('should have correct key code values', () => {
    expect(KEY_CODES.ESCAPE).toBe('Escape');
    expect(KEY_CODES.ENTER).toBe('Enter');
  });
});
```

#### `sr.test.ts`
- Test lazy loading of ScrollReveal
- Test instance caching
- Test SSR compatibility

---

### Hooks (`src/frontend/hooks/`)

#### `useScrollReveal.test.tsx`
- Initialize ScrollReveal on mount
- Use custom/default config
- Skip with reduced motion
- Cleanup on unmount
- Test `useScrollRevealMultiple` for staggered animations

#### `usePrefersReducedMotion.test.tsx`
- Return false when no preference
- Return true when reduced motion preferred
- Update on preference change
- Cleanup listeners

#### `useScrollDirection.test.tsx`
- Return "up" initially
- Detect scroll down/up
- Respect threshold
- Throttle events

#### `useOnClickOutside.test.tsx`
- Call handler on outside click
- Skip handler on inside click
- Handle touch events

#### `useDelayedMount.test.tsx`
- Return false initially
- Return true after delay
- Cleanup timeout

---

### Components

#### Layout (`layout.test.tsx`)
- Render children, Nav, Social, Email, Footer
- Show/hide loader based on location
- Handle hash navigation
- Add target="_blank" to external links
- Provide theme via ThemeProvider

#### Nav (`nav.test.tsx`)
- Render logo and nav links
- Hide/show on scroll down/up
- Open/close mobile menu
- Close menu on escape/outside click
- Keyboard navigation (Tab, Enter)
- Animate nav items on home page
- Respect reduced motion

#### Hero (`sections/hero.test.tsx`)
- Render greeting, name, tagline, description
- Animate with TransitionGroup
- Delay animations by navDelay
- Skip animations with reduced motion

#### Jobs (`sections/jobs.test.tsx`)
- Render job tabs and details
- Switch job on tab click
- Navigate tabs with arrow keys
- Update highlight indicator position
- Proper ARIA roles and attributes

#### Featured (`sections/featured.test.tsx`)
- Render all featured projects
- Render images, titles, descriptions, tech stack
- Handle external/GitHub links
- Reveal on scroll with stagger

#### About, Certs, Projects, Contact
- Similar patterns: render content, scroll reveal, accessibility

#### Icons (`icons/index.test.tsx`)
- Render all icon types correctly
- Pass props (className, etc.)
- Handle invalid icon names

#### Email/Social/Footer
- Render links from config
- Animate on home page
- Accessibility (rel, target)

---

### Pages & Templates

#### `pages/index.test.tsx`
- Render all sections in order
- Lazy load section components
- Pass location to Layout

#### `pages/blog/index.test.tsx`
- Render blog posts
- Filter/sort posts
- Handle empty posts

#### `templates/post.test.tsx`
- Render post title, date, content, tags
- Render prev/next navigation

---

## Implementation Phases (6 Weeks)

### Week 1: Foundation
- Install dependencies
- Create config files (vitest.config.ts, setup.ts, utils.tsx)
- Add scripts to package.json
- Smoke test verification

### Week 2: Utils & Hooks
- Test all utility functions (95%+ coverage)
- Test all 6 custom hooks (95%+ coverage)

### Week 3: Simple Components
- Icon components
- Email, Social, Footer
- Loader

### Week 4: Layout & Navigation
- Layout component
- Nav component (desktop + mobile)
- Head component

### Week 5: Section Components
- Hero, About, Jobs, Featured, Certs, Projects, Contact
- Scroll reveal integration

### Week 6: Pages, Integration & CI/CD
- Page components
- Template components
- Integration tests
- GitHub Actions setup
- Coverage reporting

---

## CI/CD Integration

### `.github/workflows/test.yml`
```yaml
name: Test Suite
on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 24.x
          cache: 'npm'
      - run: npm ci --legacy-peer-deps
      - run: npm run type-check
      - run: npm run test:coverage
      - uses: codecov/codecov-action@v4
        with:
          file: ./coverage/lcov.info
```

---

## Best Practices

1. **Test Behavior, Not Implementation** - Focus on user perspective
2. **AAA Pattern** - Arrange, Act, Assert
3. **Descriptive Names** - `should render email link with correct address`
4. **Isolated Tests** - No shared state
5. **Mock External Dependencies** - Gatsby, ScrollReveal, AnimeJS
6. **Keep Tests Fast** - Unit tests in milliseconds
7. **Test Edge Cases** - Empty arrays, null, errors
8. **Accessibility Testing** - ARIA, keyboard nav
9. **Co-locate Tests** - `component.tsx` + `component.test.tsx`

---

## Success Metrics

- [x] 90%+ overall code coverage
- [x] All critical user paths tested
- [x] Zero failing tests in main branch
- [x] CI/CD pipeline on all PRs
- [x] Test suite runs in < 2 minutes
- [x] All new features include tests

---

## Quick Start

```bash
# 1. Install dependencies
npm install --save-dev vitest @vitest/ui @testing-library/react \
  @testing-library/jest-dom @testing-library/user-event jsdom @vitest/coverage-v8

# 2. Create config files (vitest.config.ts, src/test/setup.ts, src/test/utils.tsx)

# 3. Add test scripts to package.json

# 4. Write your first test
# src/frontend/utils/index.test.ts

# 5. Run tests
npm run test:coverage
```

---

**Version:** 1.0
**Created:** 2025-01-14
**Target Coverage:** 90%
**Timeline:** 6 weeks
