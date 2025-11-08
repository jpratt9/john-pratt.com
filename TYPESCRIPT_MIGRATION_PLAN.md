# TypeScript Migration Plan - John Pratt Portfolio

## Executive Summary

This document provides a comprehensive, step-by-step plan for migrating the john-pratt.com portfolio website from JavaScript to TypeScript while maintaining all existing functionality. The migration will preserve React, Gatsby, GraphQL, and styled-components while adding full type safety.

**Migration Type**: COMPLETE - 100% TypeScript conversion of all application code
**Scope**: All files in `src/` directory converted to TypeScript
**Exceptions**: Gatsby config files (gatsby-*.js) remain as JavaScript for compatibility
**Estimated Timeline**: 2-3 weeks for full migration
**Risk Level**: Low-Medium (no breaking changes to functionality)
**Benefits**: Type safety, better IDE support, improved maintainability, catch bugs at compile time

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Migration Strategy](#2-migration-strategy)
3. [Phase 1: TypeScript Setup](#3-phase-1-typescript-setup)
4. [Phase 2: Type Definitions](#4-phase-2-type-definitions)
5. [Phase 3: Utilities & Hooks Migration](#5-phase-3-utilities--hooks-migration)
6. [Phase 4: Component Migration](#6-phase-4-component-migration)
7. [Phase 5: Pages & Templates Migration](#7-phase-5-pages--templates-migration)
8. [Phase 6: Gatsby Files Migration](#8-phase-6-gatsby-files-migration)
9. [Phase 7: Testing & Validation](#9-phase-7-testing--validation)
10. [Phase 8: Cleanup](#10-phase-8-cleanup)
11. [Rollback Plan](#11-rollback-plan)
12. [Post-Migration Best Practices](#12-post-migration-best-practices)

---

## 1. Prerequisites

### Required Knowledge
- TypeScript fundamentals
- React with TypeScript
- Gatsby TypeScript patterns
- GraphQL type generation
- styled-components with TypeScript

### Tools & Dependencies
```bash
# Install TypeScript and types
npm install --save-dev typescript
npm install --save-dev @types/node
npm install --save-dev @types/react
npm install --save-dev @types/react-dom
npm install --save-dev @types/lodash

# Gatsby TypeScript plugin
npm install --save-dev gatsby-plugin-typescript

# GraphQL code generation
npm install --save-dev @graphql-codegen/cli
npm install --save-dev @graphql-codegen/typescript
npm install --save-dev @graphql-codegen/typescript-operations
npm install --save-dev @graphql-codegen/typescript-react-apollo

# styled-components types
npm install --save-dev @types/styled-components
```

### Backup Strategy
```bash
# Create a new branch for migration
git checkout -b typescript-migration

# Tag current state
git tag pre-typescript-migration
```

---

## 2. Migration Strategy

### Approach: Complete TypeScript Conversion
We will use a **systematic, bottom-up** approach to convert **every single JavaScript file** to TypeScript:

1. Start with utilities and hooks (no dependencies)
2. Move to leaf components (icons, simple components)
3. Progress to complex components
4. Migrate pages and templates
5. Update Gatsby configuration files
6. **Delete all remaining `.js` files** (except config files that must be `.js`)

### Key Principles
- ✅ **Complete conversion** - NO JavaScript files remain (except required config files)
- ✅ Test each phase before moving to the next
- ✅ No functional changes, only type additions
- ✅ Commit frequently with descriptive messages
- ✅ Strict TypeScript mode enabled (`strict: true`)
- ✅ All components fully typed with proper interfaces

### File Extension Strategy
- **ALL** `.js` files → `.ts` (utilities, config, Node.js files)
- **ALL** `.js` files with JSX → `.tsx` (React components)
- Exception: Root-level config files that Gatsby/build tools require as `.js` (will document which ones)

### Files That Must Remain JavaScript
The following files **MUST** stay as `.js` files:
- `gatsby-config.js` - Gatsby configuration (DO NOT migrate)
- `gatsby-node.js` - Gatsby Node API (DO NOT migrate)
- `gatsby-ssr.js` - Gatsby SSR API (DO NOT migrate)
- `prettier.config.js` - Prettier doesn't support `.ts` config
- `.eslintrc.js` - ESLint config (if using JS format)

**Everything else in `src/`**: **FULL TYPESCRIPT CONVERSION**

**Why keep Gatsby files as JavaScript?**
- Gatsby's config system can be unreliable with TypeScript
- Keeping them as `.js` ensures maximum compatibility
- The Gatsby team recommends `.js` for config files
- These files are configuration, not application code

---

## 3. Phase 1: TypeScript Setup

### Step 1.1: Create tsconfig.json

Create `/tsconfig.json`:

```json
{
  "compilerOptions": {
    /* Language and Environment */
    "target": "ES2020",
    "lib": ["DOM", "DOM.Iterable", "ES2020"],
    "jsx": "react",

    /* Modules */
    "module": "ESNext",
    "moduleResolution": "node",
    "resolveJsonModule": true,

    /* JavaScript Support */
    "allowJs": true,
    "checkJs": false,

    /* Emit */
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "./dist",
    "removeComments": true,
    "noEmit": true,

    /* Interop Constraints */
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "forceConsistentCasingInFileNames": true,
    "isolatedModules": true,

    /* Type Checking */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "skipLibCheck": true,

    /* Path Mapping (match webpack aliases) */
    "baseUrl": ".",
    "paths": {
      "@components/*": ["src/frontend/components/*"],
      "@components": ["src/frontend/components"],
      "@config": ["src/frontend/config"],
      "@fonts/*": ["src/frontend/fonts/*"],
      "@hooks/*": ["src/frontend/hooks/*"],
      "@hooks": ["src/frontend/hooks"],
      "@images/*": ["src/frontend/images/*"],
      "@pages/*": ["src/frontend/pages/*"],
      "@styles/*": ["src/frontend/styles/*"],
      "@styles": ["src/frontend/styles"],
      "@utils/*": ["src/frontend/utils/*"],
      "@utils": ["src/frontend/utils"]
    }
  },
  "include": [
    "src/**/*"
  ],
  "exclude": [
    "node_modules",
    "public",         // Generated build output
    ".cache",         // Gatsby cache (generated)
    "dist"            // Build artifacts
  ]
}
```

### Step 1.2: Add gatsby-plugin-typescript

Update `gatsby-config.js`:

```javascript
module.exports = {
  plugins: [
    'gatsby-plugin-typescript',
    // ... existing plugins
  ]
}
```

### Step 1.3: Create Type Declaration Files

Create `src/types/global.d.ts`:

```typescript
/// <reference types="node" />
/// <reference types="react" />
/// <reference types="react-dom" />

declare module '*.png' {
  const value: string;
  export default value;
}

declare module '*.jpg' {
  const value: string;
  export default value;
}

declare module '*.jpeg' {
  const value: string;
  export default value;
}

declare module '*.svg' {
  import * as React from 'react';
  export const ReactComponent: React.FunctionComponent<
    React.SVGProps<SVGSVGElement> & { title?: string }
  >;
  const src: string;
  export default src;
}

declare module '*.webp' {
  const value: string;
  export default value;
}

declare module '*.avif' {
  const value: string;
  export default value;
}
```

Create `src/types/styled.d.ts`:

```typescript
import 'styled-components';
import { Theme } from '../frontend/styles/theme';

declare module 'styled-components' {
  export interface DefaultTheme extends Theme {}
}
```

### Step 1.4: Update package.json Scripts

```json
{
  "scripts": {
    "type-check": "tsc --noEmit",
    "type-check:watch": "tsc --noEmit --watch",
    "build": "npm run type-check && gatsby build",
    "develop": "gatsby develop",
    "format": "prettier --write \"**/*.{ts,tsx,json,md}\"",
    "lint": "eslint . --ext .ts,.tsx",
    "verify-no-js": "bash -c 'JS_COUNT=$(find src -name \"*.js\" -type f | wc -l); if [ $JS_COUNT -eq 0 ]; then echo \"✅ No JavaScript files in src/\"; else echo \"❌ Found $JS_COUNT JavaScript files in src/:\"; find src -name \"*.js\" -type f; exit 1; fi'"
  }
}
```

**Note Changes:**
- `format`: Removed `.js,.jsx` - only TypeScript files now
- `lint`: Removed `.js,.jsx` - only TypeScript files now
- `verify-no-js`: New script to ensure complete migration

### Step 1.5: Update ESLint Configuration

Create `.eslintrc.js` (if not exists) or update existing:

```javascript
module.exports = {
  parser: '@typescript-eslint/parser',
  extends: [
    'plugin:react/recommended',
    'plugin:@typescript-eslint/recommended',
    'prettier',
  ],
  plugins: ['react', '@typescript-eslint'],
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
  },
  rules: {
    'react/prop-types': 'off', // We'll use TypeScript instead
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    '@typescript-eslint/no-explicit-any': 'warn',
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
};
```

Install additional dependencies:

```bash
npm install --save-dev @typescript-eslint/parser @typescript-eslint/eslint-plugin
```

### Step 1.6: GraphQL Code Generation Setup

Create `codegen.yml`:

```yaml
overwrite: true
schema: "http://localhost:8000/___graphql"
documents: "src/**/*.{ts,tsx}"
generates:
  src/types/graphql.ts:
    plugins:
      - typescript
      - typescript-operations
    config:
      avoidOptionals: false
      maybeValue: T | null
      skipTypename: false
```

Add script to `package.json`:

```json
{
  "scripts": {
    "codegen": "graphql-codegen --config codegen.yml",
    "codegen:watch": "graphql-codegen --config codegen.yml --watch"
  }
}
```

---

## 4. Phase 2: Type Definitions

### Step 2.1: Create Common Type Definitions

Create `src/types/index.ts`:

```typescript
import { IGatsbyImageData } from 'gatsby-plugin-image';

// Location object from Gatsby
export interface Location {
  pathname: string;
  search: string;
  hash: string;
  href: string;
  origin: string;
  protocol: string;
  host: string;
  hostname: string;
  port: string;
  state?: unknown;
  key?: string;
}

// Page context from Gatsby
export interface PageContext {
  [key: string]: unknown;
}

// Page props
export interface PageProps<TData = unknown, TContext = PageContext> {
  location: Location;
  pageContext: TContext;
  data?: TData;
  children?: React.ReactNode;
}

// Config types
export interface SocialMedia {
  name: string;
  url: string;
}

export interface NavLink {
  name: string;
  url: string;
}

export interface SiteConfig {
  email: string;
  socialMedia: SocialMedia[];
  navLinks: NavLink[];
  colors: {
    green: string;
    navy: string;
    darkNavy: string;
  };
  srConfig: (delay?: number, viewFactor?: number) => ScrollRevealConfig;
}

export interface ScrollRevealConfig {
  origin: string;
  distance: string;
  duration: number;
  delay: number;
  rotate: { x: number; y: number; z: number };
  opacity: number;
  scale: number;
  easing: string;
  mobile: boolean;
  reset: boolean;
  useDelay: string;
  viewFactor: number;
  viewOffset: { top: number; right: number; bottom: number; left: number };
}

// Markdown frontmatter types
export interface JobFrontmatter {
  title: string;
  company: string;
  location: string;
  range: string;
  url: string;
  companyRank?: number;
}

export interface CertFrontmatter {
  title: string;
  certRank: number;
  company: string;
  issueDate: string;
  expiryDate?: string;
  url: string;
  show?: boolean;
  companyRank?: number;
}

export interface FeaturedProjectFrontmatter {
  title: string;
  cover: {
    childImageSharp: {
      gatsbyImageData: IGatsbyImageData;
    };
  };
  tech: string[];
  classified?: boolean;
  github?: string;
  external?: string;
  date?: string;
}

export interface BlogPostFrontmatter {
  title: string;
  slug: string;
  date: string;
  tags: string[];
  draft?: boolean;
}

// GraphQL node types
export interface MarkdownNode<T> {
  frontmatter: T;
  html: string;
}

export interface GraphQLEdge<T> {
  node: MarkdownNode<T>;
}

export interface GraphQLConnection<T> {
  edges: GraphQLEdge<T>[];
}

// Hook return types
export type ScrollDirection = 'up' | 'down';

export interface UseScrollDirectionOptions {
  initialDirection?: ScrollDirection;
  thresholdPixels?: number;
  off?: boolean;
}
```

### Step 2.2: Create Theme Types

Create `src/types/theme.d.ts`:

```typescript
export interface Theme {
  mixins: {
    flexCenter: string;
    flexBetween: string;
    link: string;
    inlineLink: string;
    button: string;
    smallButton: string;
    bigButton: string;
    boxShadow: string;
    fancyList: string;
    resetList: string;
  };
}
```

### Step 2.3: Update Theme File

Update `src/frontend/styles/theme.js` to `theme.ts`:

```typescript
import { css, DefaultTheme, CSSObject } from 'styled-components';

const theme: DefaultTheme = {
  mixins: {
    flexCenter: css`
      display: flex;
      justify-content: center;
      align-items: center;
    ` as unknown as string,

    flexBetween: css`
      display: flex;
      justify-content: space-between;
      align-items: center;
    ` as unknown as string,

    // ... other mixins
  },
};

export default theme;
export type { DefaultTheme as Theme };
```

---

## 5. Phase 3: Utilities & Hooks Migration

### Step 3.1: Migrate Config File

**Before** (`src/frontend/config.js`):
```javascript
module.exports = {
  email: 'john@john-pratt.com',
  socialMedia: [ /* ... */ ],
  // ...
};
```

**After** (`src/frontend/config.ts`):
```typescript
import { SiteConfig } from '../types';

const config: SiteConfig = {
  email: 'john@john-pratt.com',
  socialMedia: [
    {
      name: 'GitHub',
      url: 'https://github.com/jpratt9',
    },
    {
      name: 'Linkedin',
      url: 'https://www.linkedin.com/in/john-pratt787',
    },
  ],
  navLinks: [
    {
      name: 'About',
      url: '/#about',
    },
    {
      name: 'Experience',
      url: '/#jobs',
    },
    {
      name: 'Projects',
      url: '/#projects',
    },
    {
      name: 'Blog',
      url: '/blog',
    },
    {
      name: 'Resume',
      url: '/resume.pdf',
    },
  ],
  colors: {
    green: '#64ffda',
    navy: '#0a192f',
    darkNavy: '#020c1b',
  },
  srConfig: (delay = 200, viewFactor = 0.25) => ({
    origin: 'bottom',
    distance: '20px',
    duration: 500,
    delay,
    rotate: { x: 0, y: 0, z: 0 },
    opacity: 0,
    scale: 1,
    easing: 'cubic-bezier(0.645, 0.045, 0.355, 1)',
    mobile: true,
    reset: false,
    useDelay: 'always',
    viewFactor,
    viewOffset: { top: 0, right: 0, bottom: 0, left: 0 },
  }),
};

export default config;
```

### Step 3.2: Migrate Utils

**Before** (`src/frontend/utils/index.js`):
```javascript
export const KEY_CODES = {
  ARROW_UP: 'ArrowUp',
  ARROW_DOWN: 'ArrowDown',
  // ...
};

export const loaderDelay = 2000;
```

**After** (`src/frontend/utils/index.ts`):
```typescript
export const KEY_CODES = {
  ARROW_UP: 'ArrowUp',
  ARROW_DOWN: 'ArrowDown',
  // ...
} as const;

export type KeyCode = typeof KEY_CODES[keyof typeof KEY_CODES];

export const loaderDelay = 2000;
```

**Before** (`src/frontend/utils/sr.js`):
```javascript
let instance;
export async function getSr() {
  if (typeof window === 'undefined') return null;
  if (instance) return instance;
  const { default: ScrollReveal } = await import('scrollreveal');
  instance = ScrollReveal();
  return instance;
}
```

**After** (`src/frontend/utils/sr.ts`):
```typescript
import scrollReveal from 'scrollreveal';

let instance: scrollReveal.ScrollRevealObject | null = null;

export async function getSr(): Promise<scrollReveal.ScrollRevealObject | null> {
  if (typeof window === 'undefined') return null;
  if (instance) return instance;

  const { default: ScrollReveal } = await import('scrollreveal');
  instance = ScrollReveal();
  return instance;
}
```

Install type definitions:
```bash
npm install --save-dev @types/scrollreveal
```

### Step 3.3: Migrate Custom Hooks

**Before** (`src/frontend/hooks/useScrollDirection.js`):
```javascript
const useScrollDirection = ({ initialDirection, thresholdPixels, off } = {}) => {
  const [scrollDir, setScrollDir] = useState(initialDirection);
  // ...
  return scrollDir;
};
```

**After** (`src/frontend/hooks/useScrollDirection.ts`):
```typescript
import { useState, useEffect } from 'react';
import { ScrollDirection, UseScrollDirectionOptions } from '../../types';

const SCROLL_UP: ScrollDirection = 'up';
const SCROLL_DOWN: ScrollDirection = 'down';

const useScrollDirection = (
  options: UseScrollDirectionOptions = {}
): ScrollDirection => {
  const { initialDirection = SCROLL_DOWN, thresholdPixels = 0, off = false } = options;
  const [scrollDir, setScrollDir] = useState<ScrollDirection>(initialDirection);

  useEffect(() => {
    const threshold = thresholdPixels;
    let lastScrollY = window.pageYOffset;
    let ticking = false;

    const updateScrollDir = () => {
      const scrollY = window.pageYOffset;

      if (Math.abs(scrollY - lastScrollY) < threshold) {
        ticking = false;
        return;
      }

      setScrollDir(scrollY > lastScrollY ? SCROLL_DOWN : SCROLL_UP);
      lastScrollY = scrollY > 0 ? scrollY : 0;
      ticking = false;
    };

    const onScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(updateScrollDir);
        ticking = true;
      }
    };

    if (!off) {
      window.addEventListener('scroll', onScroll);
    } else {
      setScrollDir(initialDirection);
    }

    return () => window.removeEventListener('scroll', onScroll);
  }, [initialDirection, thresholdPixels, off]);

  return scrollDir;
};

export default useScrollDirection;
```

**Before** (`src/frontend/hooks/usePrefersReducedMotion.js`):
```javascript
const usePrefersReducedMotion = () => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  // ...
  return prefersReducedMotion;
};
```

**After** (`src/frontend/hooks/usePrefersReducedMotion.ts`):
```typescript
import { useState, useEffect } from 'react';

const QUERY = '(prefers-reduced-motion: no-preference)';

const usePrefersReducedMotion = (): boolean => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState<boolean>(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const mediaQueryList = window.matchMedia(QUERY);
    setPrefersReducedMotion(!mediaQueryList.matches);

    const listener = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(!event.matches);
    };

    if (mediaQueryList.addEventListener) {
      mediaQueryList.addEventListener('change', listener);
    } else {
      // Fallback for older browsers
      mediaQueryList.addListener(listener);
    }

    return () => {
      if (mediaQueryList.removeEventListener) {
        mediaQueryList.removeEventListener('change', listener);
      } else {
        mediaQueryList.removeListener(listener);
      }
    };
  }, []);

  return prefersReducedMotion;
};

export default usePrefersReducedMotion;
```

**Before** (`src/frontend/hooks/useOnClickOutside.js`):
```javascript
const useOnClickOutside = (ref, handler) => {
  useEffect(() => {
    const listener = (event) => {
      // ...
    };
    // ...
  }, [ref, handler]);
};
```

**After** (`src/frontend/hooks/useOnClickOutside.ts`):
```typescript
import { useEffect, RefObject } from 'react';

const useOnClickOutside = (
  ref: RefObject<HTMLElement>,
  handler: (event: MouseEvent | TouchEvent) => void
): void => {
  useEffect(() => {
    const listener = (event: MouseEvent | TouchEvent) => {
      if (!ref.current || ref.current.contains(event.target as Node)) {
        return;
      }
      handler(event);
    };

    document.addEventListener('mousedown', listener);
    document.addEventListener('touchstart', listener);

    return () => {
      document.removeEventListener('mousedown', listener);
      document.removeEventListener('touchstart', listener);
    };
  }, [ref, handler]);
};

export default useOnClickOutside;
```

**Update** (`src/frontend/hooks/index.ts`):
```typescript
export { default as useScrollDirection } from './useScrollDirection';
export { default as usePrefersReducedMotion } from './usePrefersReducedMotion';
export { default as useOnClickOutside } from './useOnClickOutside';
```

---

## 6. Phase 4: Component Migration

### Step 4.1: Migration Order

1. **Icon components** (simplest, no dependencies)
2. **Simple components** (Head, Email, Social, Footer)
3. **Complex components** (Nav, Menu, Layout)
4. **Section components** (Hero, About, Jobs, Featured, Certs, Contact)

### Step 4.2: Icon Components Example

**Before** (`src/frontend/components/icons/github.js`):
```javascript
const IconGitHub = () => (
  <svg /* ... */ >
    {/* ... */}
  </svg>
);

export default IconGitHub;
```

**After** (`src/frontend/components/icons/github.tsx`):
```typescript
import React from 'react';

const IconGitHub: React.FC = () => (
  <svg /* ... */ >
    {/* ... */}
  </svg>
);

export default IconGitHub;
```

### Step 4.3: Components with Props Example

**Before** (`src/frontend/components/nav.js`):
```javascript
import PropTypes from 'prop-types';

const Nav = ({ isHome }) => {
  // ...
};

Nav.propTypes = {
  isHome: PropTypes.bool,
};

export default Nav;
```

**After** (`src/frontend/components/nav.tsx`):
```typescript
import React, { useState, useEffect, FC } from 'react';
import { Link } from 'gatsby';
import { CSSTransition, TransitionGroup } from 'react-transition-group';
import styled, { css } from 'styled-components';
import { navLinks } from '@config';
import { loaderDelay } from '@utils';
import { useScrollDirection, usePrefersReducedMotion } from '@hooks';
import { Menu } from '@components';
import { IconLogo, IconHex } from '@components/icons';

interface NavProps {
  isHome?: boolean;
}

interface StyledHeaderProps {
  scrollDirection: string;
  scrolledToTop: boolean;
}

const StyledHeader = styled.header<StyledHeaderProps>`
  ${({ theme }) => theme.mixins.flexBetween};
  position: fixed;
  top: 0;
  z-index: 11;
  padding: 0px 50px;
  width: 100%;
  height: var(--nav-height);
  background-color: rgba(10, 25, 47, 0.85);
  filter: none !important;
  pointer-events: auto !important;
  user-select: auto !important;
  backdrop-filter: blur(10px);
  transition: var(--transition);

  @media (max-width: 1080px) {
    padding: 0 40px;
  }
  @media (max-width: 768px) {
    padding: 0 25px;
  }

  @media (prefers-reduced-motion: no-preference) {
    ${props =>
      !props.scrolledToTop &&
      css`
        height: var(--nav-scroll-height);
        background-color: rgba(10, 25, 47, 0.85);
        box-shadow: 0 10px 30px -10px var(--navy-shadow);
      `};
  }
`;

const Nav: FC<NavProps> = ({ isHome = false }) => {
  const [isMounted, setIsMounted] = useState<boolean>(!isHome);
  const scrollDirection = useScrollDirection({ initialDirection: 'down' });
  const [scrolledToTop, setScrolledToTop] = useState<boolean>(true);
  const prefersReducedMotion = usePrefersReducedMotion();

  const handleScroll = (): void => {
    setScrolledToTop(window.pageYOffset < 50);
  };

  useEffect(() => {
    if (prefersReducedMotion) {
      return;
    }

    const timeout = setTimeout(() => {
      setIsMounted(true);
    }, 100);

    window.addEventListener('scroll', handleScroll);

    return () => {
      clearTimeout(timeout);
      window.removeEventListener('scroll', handleScroll);
    };
  }, [prefersReducedMotion]);

  // ... rest of component

  return (
    <StyledHeader scrollDirection={scrollDirection} scrolledToTop={scrolledToTop}>
      {/* ... */}
    </StyledHeader>
  );
};

export default Nav;
```

### Step 4.4: Layout Component

**After** (`src/frontend/components/layout.tsx`):
```typescript
import React, { useState, useEffect, lazy, Suspense, FC, ReactNode } from 'react';
import styled, { ThemeProvider } from 'styled-components';
import { Head, Nav, Social, Email, Footer } from '@components';
import { GlobalStyle, theme } from '@styles';
import { Location } from '../../types';

const Loader = lazy(() => import('./loader'));

interface LayoutProps {
  children: ReactNode;
  location: Location;
}

const StyledContent = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
`;

const Layout: FC<LayoutProps> = ({ children, location }) => {
  const isHome = location.pathname === '/';
  const [isLoading, setIsLoading] = useState<boolean>(isHome);

  const handleExternalLinks = (): void => {
    const allLinks = Array.from(document.querySelectorAll('a'));
    if (allLinks.length > 0) {
      allLinks.forEach(link => {
        if (link.host !== window.location.host) {
          link.setAttribute('rel', 'noopener noreferrer');
          link.setAttribute('target', '_blank');
        }
      });
    }
  };

  useEffect(() => {
    if (isLoading) return;

    if (location.hash) {
      const id = location.hash.substring(1);
      setTimeout(() => {
        const el = document.getElementById(id);
        if (el) {
          el.scrollIntoView({ behavior: 'smooth', block: 'start' });
          el.focus();
        }
      }, 0);
    }

    handleExternalLinks();
  }, [isLoading, location.hash]);

  return (
    <>
      <Head />
      <div id="root">
        <ThemeProvider theme={theme}>
          <GlobalStyle />
          <a className="skip-to-content" href="#content">
            Skip to Content
          </a>
          {isLoading && isHome ? (
            <Suspense fallback={null}>
              <Loader finishLoading={() => setIsLoading(false)} />
            </Suspense>
          ) : (
            <StyledContent>
              <Nav isHome={isHome} />
              <Social isHome={isHome} />
              <Email isHome={isHome} />
              <div id="content">
                {children}
                <Footer />
              </div>
            </StyledContent>
          )}
        </ThemeProvider>
      </div>
    </>
  );
};

export default Layout;
```

### Step 4.5: Section Components with GraphQL

**After** (`src/frontend/components/sections/jobs.tsx`):
```typescript
import React, { useState, useEffect, useRef, FC } from 'react';
import { useStaticQuery, graphql } from 'gatsby';
import { CSSTransition } from 'react-transition-group';
import styled from 'styled-components';
import { srConfig } from '@config';
import { KEY_CODES } from '@utils';
import { getSr } from '@utils/sr';
import { usePrefersReducedMotion } from '@hooks';
import { JobFrontmatter, MarkdownNode, GraphQLConnection } from '../../../types';

interface JobsData {
  jobs: GraphQLConnection<JobFrontmatter>;
}

interface StyledTabButtonProps {
  isActive: boolean;
}

interface StyledHighlightProps {
  activeTabId: number;
}

const StyledTabButton = styled.button<StyledTabButtonProps>`
  ${({ theme }) => theme.mixins.link};
  display: flex;
  align-items: center;
  width: 100%;
  height: var(--tab-height);
  padding: 0 20px 2px;
  border-left: 2px solid var(--lightest-navy);
  background-color: transparent;
  color: ${({ isActive }) => (isActive ? 'var(--green)' : 'var(--slate)')};
  font-family: var(--font-mono);
  font-size: var(--fz-xs);
  text-align: left;
  white-space: nowrap;

  &:hover,
  &:focus {
    background-color: var(--light-navy);
  }
`;

const Jobs: FC = () => {
  const data = useStaticQuery<JobsData>(graphql`
    query {
      jobs: allMarkdownRemark(
        filter: { fileAbsolutePath: { regex: "/src/frontend/content/jobs/" } }
        sort: { frontmatter: { companyRank: ASC } }
      ) {
        edges {
          node {
            frontmatter {
              title
              company
              location
              range
              url
            }
            html
          }
        }
      }
    }
  `);

  const jobsData = data.jobs.edges;
  const [activeTabId, setActiveTabId] = useState<number>(0);
  const [tabFocus, setTabFocus] = useState<number | null>(null);
  const tabs = useRef<(HTMLButtonElement | null)[]>([]);
  const revealContainer = useRef<HTMLElement>(null);
  const prefersReducedMotion = usePrefersReducedMotion();

  useEffect(() => {
    if (prefersReducedMotion) return;

    let mounted = true;

    (async () => {
      const sr = await getSr();
      if (!mounted || !sr) return;
      if (revealContainer.current) {
        sr.reveal(revealContainer.current, srConfig());
      }
    })();

    return () => {
      mounted = false;
    };
  }, [prefersReducedMotion]);

  const focusTab = (): void => {
    if (tabFocus !== null && tabs.current[tabFocus]) {
      tabs.current[tabFocus]?.focus();
      return;
    }
    if (tabFocus !== null && tabFocus >= tabs.current.length) {
      setTabFocus(0);
    }
    if (tabFocus !== null && tabFocus < 0) {
      setTabFocus(tabs.current.length - 1);
    }
  };

  useEffect(() => {
    focusTab();
  }, [tabFocus]);

  const onKeyDown = (e: React.KeyboardEvent): void => {
    switch (e.key) {
      case KEY_CODES.ARROW_UP:
        e.preventDefault();
        setTabFocus(tabFocus !== null ? tabFocus - 1 : 0);
        break;
      case KEY_CODES.ARROW_DOWN:
        e.preventDefault();
        setTabFocus(tabFocus !== null ? tabFocus + 1 : 0);
        break;
      default:
        break;
    }
  };

  // ... rest of component with proper typing

  return (
    <section id="jobs" ref={revealContainer}>
      {/* ... */}
    </section>
  );
};

export default Jobs;
```

---

## 7. Phase 5: Pages & Templates Migration

### Step 5.1: Homepage

**After** (`src/frontend/pages/index.tsx`):
```typescript
import React, { lazy, Suspense, FC } from 'react';
import styled from 'styled-components';
import { Layout, Hero } from '@components';
import { PageProps } from '../../types';

const About = lazy(() => import('@components/sections/about'));
const Jobs = lazy(() => import('@components/sections/jobs'));
const Featured = lazy(() => import('@components/sections/featured'));
const Certs = lazy(() => import('@components/sections/certs'));
const Projects = lazy(() => import('@components/sections/projects'));
const Contact = lazy(() => import('@components/sections/contact'));

const StyledMainContainer = styled.main`
  counter-reset: section;
`;

const IndexPage: FC<PageProps> = ({ location }) => (
  <Layout location={location}>
    <StyledMainContainer className="fillHeight">
      <Hero />
      <Suspense fallback={null}>
        <About />
        <Jobs />
        <Featured />
        <Certs />
        <Projects />
        <Contact />
      </Suspense>
    </StyledMainContainer>
  </Layout>
);

export default IndexPage;
```

### Step 5.2: Blog Pages

**After** (`src/frontend/pages/blog/index.tsx`):
```typescript
import React, { FC } from 'react';
import { graphql, Link } from 'gatsby';
import kebabCase from 'lodash/kebabCase';
import styled from 'styled-components';
import { Layout } from '@components';
import { IconBookmark } from '@components/icons';
import SEO from '@components/head';
import { PageProps, BlogPostFrontmatter, GraphQLConnection } from '../../../types';

interface BlogPageData {
  allMarkdownRemark: GraphQLConnection<BlogPostFrontmatter>;
}

const BlogPage: FC<PageProps<BlogPageData>> = ({ location, data }) => {
  const posts = data.allMarkdownRemark.edges;

  return (
    <Layout location={location}>
      {/* ... */}
    </Layout>
  );
};

export default BlogPage;

export function Head({ location }: Pick<PageProps, 'location'>) {
  return (
    <SEO
      title="Blog"
      description="Notes from the Field: Building, Thinking, Iterating"
      pathname={location?.pathname}
    />
  );
}

export const pageQuery = graphql`
  {
    allMarkdownRemark(
      filter: {
        fileAbsolutePath: { regex: "/src/frontend/content/posts/" }
        frontmatter: { draft: { ne: true } }
      }
      sort: { frontmatter: { date: DESC } }
    ) {
      edges {
        node {
          frontmatter {
            title
            slug
            date
            tags
            draft
          }
          html
        }
      }
    }
  }
`;
```

### Step 5.3: Blog Post Template

**After** (`src/frontend/templates/post.tsx`):
```typescript
import React, { FC } from 'react';
import { graphql, Link } from 'gatsby';
import kebabCase from 'lodash/kebabCase';
import styled from 'styled-components';
import { Layout } from '@components';
import SEO from '@components/head';
import { createGlobalStyle } from 'styled-components';
import PrismStyles from '@styles/PrismStyles';
import { PageProps, BlogPostFrontmatter, MarkdownNode } from '../../types';

const PrismGlobal = createGlobalStyle`${PrismStyles}`;

interface PostTemplateData {
  markdownRemark: MarkdownNode<BlogPostFrontmatter>;
}

const PostTemplate: FC<PageProps<PostTemplateData>> = ({ data, location }) => {
  const post = data?.markdownRemark;
  if (!post) return null;

  const { frontmatter, html } = post;
  const { title, tags, draft } = frontmatter;

  return (
    <Layout location={location}>
      <PrismGlobal />
      {/* ... */}
    </Layout>
  );
};

export default PostTemplate;

export function Head({ data, location }: PageProps<PostTemplateData>) {
  const fm = data?.markdownRemark?.frontmatter;
  return <SEO title={fm?.title} pathname={location?.pathname} />;
}

export const pageQuery = graphql`
  query ($slug: String!) {
    markdownRemark(frontmatter: { slug: { eq: $slug } }) {
      html
      frontmatter {
        title
        draft
        date
        slug
        tags
      }
    }
  }
`;
```

---

## 8. Phase 6: Gatsby Files - DO NOT MIGRATE

### Important: Keep Gatsby Config Files as JavaScript

**DO NOT** migrate the following files to TypeScript:
- `gatsby-config.js` - Keep as `.js`
- `gatsby-node.js` - Keep as `.js`
- `gatsby-ssr.js` - Keep as `.js`

### Why Keep These as JavaScript?

1. **Gatsby Compatibility**: Gatsby's config system works best with JavaScript
2. **Tool Compatibility**: Many Gatsby plugins expect `.js` config files
3. **Simplicity**: These are configuration files, not application code
4. **Official Recommendation**: Gatsby docs recommend `.js` for config files
5. **Avoid Edge Cases**: TypeScript in Gatsby config can cause subtle issues

### What You CAN Do (Optional)

If you want type safety in Gatsby files, you can use JSDoc comments:

**Example** (`gatsby-node.js` with JSDoc):
```javascript
const path = require('path');
const _ = require('lodash');
const fs = require('fs');
const fsp = fs.promises;

/**
 * @type {import('gatsby').GatsbyNode['createPages']}
 */
exports.createPages = async ({ actions, graphql, reporter }) => {
  const { createPage, createRedirect } = actions;
  const postTemplate = path.resolve(`src/frontend/templates/post.tsx`);
  const tagTemplate = path.resolve('src/frontend/templates/tag.tsx');

  const result = await graphql(`
    {
      postsRemark: allMarkdownRemark(
        filter: { fileAbsolutePath: { regex: "/src/frontend/content/posts/" } }
        sort: { frontmatter: { date: DESC } }
        limit: 1000
      ) {
        edges {
          node {
            frontmatter {
              slug
              tags
            }
          }
        }
      }
    }
  `);

  if (result.errors) {
    reporter.panicOnBuild(`Error while running GraphQL query.`);
    return;
  }

  const posts = result.data.postsRemark?.edges || [];

  // Create individual post pages
  posts.forEach(({ node }) => {
    const pathFromFM = node.frontmatter?.slug;
    if (!pathFromFM) return;

    createPage({
      path: pathFromFM,
      component: postTemplate,
      context: { slug: pathFromFM },
    });
  });

  // Create tag pages
  const tagsByKey = new Map();
  posts.forEach(({ node }) => {
    const tags = node.frontmatter?.tags || [];
    tags.forEach((t) => {
      if (typeof t !== 'string') return;
      const raw = t.trim();
      if (!raw) return;
      const key = _.kebabCase(raw);
      if (!tagsByKey.has(key)) tagsByKey.set(key, new Set());
      tagsByKey.get(key).add(raw);
    });
  });

  for (const [key, set] of tagsByKey.entries()) {
    const variants = Array.from(set);
    const display = variants[0];
    createPage({
      path: `/blog/tags/${key}/`,
      component: tagTemplate,
      context: { tag: display },
    });
  }

  createRedirect({
    fromPath: '/archive',
    toPath: '/blog',
    isPermanent: true,
  });
};

/**
 * @type {import('gatsby').GatsbyNode['onCreateWebpackConfig']}
 */
exports.onCreateWebpackConfig = ({ stage, loaders, actions }) => {
  if (stage === 'build-html' || stage === 'develop-html') {
    actions.setWebpackConfig({
      module: {
        rules: [
          { test: /scrollreveal/, use: loaders.null() },
          { test: /animejs/, use: loaders.null() },
          { test: /miniraf/, use: loaders.null() },
        ],
      },
    });
  }

  actions.setWebpackConfig({
    resolve: {
      alias: {
        '@components': path.resolve(__dirname, 'src/frontend/components'),
        '@config': path.resolve(__dirname, 'src/frontend/config'),
        '@fonts': path.resolve(__dirname, 'src/frontend/fonts'),
        '@hooks': path.resolve(__dirname, 'src/frontend/hooks'),
        '@images': path.resolve(__dirname, 'src/frontend/images'),
        '@pages': path.resolve(__dirname, 'src/frontend/pages'),
        '@styles': path.resolve(__dirname, 'src/frontend/styles'),
        '@utils': path.resolve(__dirname, 'src/frontend/utils'),
      },
      extensions: ['.mjs', '.js', '.jsx', '.ts', '.tsx', '.json'],
    },
  });
};

/**
 * @type {import('gatsby').GatsbyNode['onPostBuild']}
 */
exports.onPostBuild = async ({ reporter }) => {
  const sourceDir = path.resolve(__dirname, 'src/frontend/static');
  const destDir = path.resolve(__dirname, 'public');

  try {
    await fsp.access(sourceDir);
  } catch (error) {
    reporter.warn(`[gatsby-node] Static directory not found at ${sourceDir}; skipping copy.`);
    return;
  }

  try {
    const entries = await fsp.readdir(sourceDir, { withFileTypes: true });

    await Promise.all(
      entries.map(async (entry) => {
        const sourcePath = path.join(sourceDir, entry.name);
        const destPath = path.join(destDir, entry.name);

        if (entry.isDirectory()) {
          await fsp.cp(sourcePath, destPath, { recursive: true });
        } else {
          await fsp.copyFile(sourcePath, destPath);
        }
      })
    );

    reporter.info(`[gatsby-node] Copied ${entries.length} asset(s) from src/frontend/static to public.`);
  } catch (error) {
    reporter.panic(`[gatsby-node] Failed to copy static assets from ${sourceDir}`, error);
  }
};
```

**Benefits of JSDoc approach:**
- ✅ Type checking via `@type` annotations
- ✅ IDE autocomplete and IntelliSense
- ✅ Keeps file as `.js` for maximum compatibility
- ✅ No TypeScript compilation needed for config files

### Summary

**Keep these files as `.js`:**
- `gatsby-config.js`
- `gatsby-node.js`
- `gatsby-ssr.js`

**Optional**: Add JSDoc comments for type safety without changing to `.ts`

**Everything in `src/` directory**: Full TypeScript conversion

---

## 9. Phase 7: Testing & Validation

### Step 7.1: Verify Complete Migration

```bash
# FIRST: Verify NO JavaScript files remain in source
npm run verify-no-js

# Should output: ✅ No JavaScript files in src/
# If it fails, you have .js files that need migration
```

### Step 7.2: Type Checking

```bash
# Run type check
npm run type-check

# Fix any errors
# Common issues:
# - Missing null checks
# - Incorrect prop types
# - GraphQL query mismatches
```

### Step 7.3: Build Test

```bash
# Clean cache
npm run clean

# Build production
npm run build

# Test locally
npm run serve
```

### Step 7.4: Manual Testing Checklist

- [ ] Homepage loads correctly
- [ ] All sections render (About, Jobs, Featured, Certs, Projects, Contact)
- [ ] Navigation works (header, mobile menu)
- [ ] Blog index loads
- [ ] Individual blog posts load
- [ ] Tag pages work
- [ ] Links work correctly
- [ ] Images load properly
- [ ] Animations work
- [ ] Responsive design intact
- [ ] Forms work (if any)
- [ ] SEO meta tags present

### Step 7.5: Performance Check

```bash
# Analyze bundle
ANALYZE_BUNDLE=true npm run build

# Check bundle size hasn't increased significantly
# TypeScript types are stripped at build time
```

---

## 10. Phase 8: Cleanup

### Step 10.1: Remove PropTypes

```bash
# After migration is complete
npm uninstall prop-types
npm uninstall @types/prop-types
```

Remove all PropTypes declarations from components.

### Step 10.2: Update Documentation

- Update README with TypeScript info
- Add TypeScript badge
- Document type generation commands
- Add contribution guidelines for TypeScript

### Step 10.3: Delete ALL JavaScript Files

**CRITICAL**: After all phases complete, verify and DELETE every single `.js` file:

```bash
# Find all remaining .js files in src/
find src -name "*.js" -type f

# Expected to find: ZERO files
# If any files are found, migrate them or understand why they exist

# Verify build still works
npm run clean
npm run build

# Double-check: Find ALL .js files outside generated directories
# Expected: Only gatsby-*.js and config files
find . -name "*.js" -type f \
  -not -path "./node_modules/*" \
  -not -path "./.cache/*" \
  -not -path "./public/*" \
  -not -name "gatsby-*.js" \
  -not -name "prettier.config.js" \
  -not -name ".eslintrc.js"

# This should return NOTHING (0 files)
```

**Final Source Code Status:**
- ✅ ALL components: `.tsx`
- ✅ ALL utilities/hooks: `.ts`
- ✅ ALL pages: `.tsx`
- ✅ ALL templates: `.tsx`
- ⚠️ Gatsby config files: `.js` (gatsby-node.js, gatsby-config.js, gatsby-ssr.js) - **DO NOT MIGRATE**
- ⚠️ Tool config files: `.js` (prettier.config.js, .eslintrc.js) - if required by those tools

**Directories that are GENERATED (not source code):**
- `public/` - Gatsby build output (contains .js, .html, etc.)
- `.cache/` - Gatsby cache
- `node_modules/` - Dependencies

These generated directories will contain JavaScript - that's expected and correct.

---

## 11. Rollback Plan

### If Migration Fails

Since this is a complete conversion, rollback is all-or-nothing:

```bash
# Complete rollback to pre-migration state
git checkout master
git branch -D typescript-migration

# Or if already merged to master
git revert <merge-commit-hash>

# Return to tagged state
git reset --hard pre-typescript-migration
```

### Emergency Fix During Migration

If you encounter a blocking issue mid-migration:

1. **DO NOT** revert individual files to `.js` - this defeats the purpose
2. **DO** fix the TypeScript error properly with correct types
3. **DO** use `@ts-expect-error` as a TEMPORARY measure with a TODO comment
4. **DO** commit your progress and take a break if needed

```typescript
// TEMPORARY: Fix this typing issue - see issue #123
// @ts-expect-error - Will fix in next commit
const result = problematicCode();
```

### Testing Before Full Commit

Before merging to master:
1. Complete ALL migration phases
2. Verify `find src -name "*.js"` returns ZERO files
3. Full build succeeds: `npm run build`
4. Type check passes: `npm run type-check`
5. All pages load correctly
6. Manual testing complete

**Only merge when 100% complete - no partial states**

---

## 12. Post-Migration Best Practices

### Code Standards

1. **Always define types explicitly**:
   ```typescript
   // Good
   const name: string = 'John';

   // Avoid
   const name = 'John'; // Type inference is fine for simple cases
   ```

2. **Use interfaces for objects**:
   ```typescript
   interface User {
     name: string;
     email: string;
   }
   ```

3. **Use type for unions**:
   ```typescript
   type Status = 'active' | 'inactive' | 'pending';
   ```

4. **Avoid `any`**:
   ```typescript
   // Bad
   const data: any = fetchData();

   // Good
   const data: ApiResponse = fetchData();
   ```

5. **Use generics for reusable components**:
   ```typescript
   interface ListProps<T> {
     items: T[];
     renderItem: (item: T) => React.ReactNode;
   }
   ```

### GraphQL Types

Always regenerate GraphQL types when queries change:

```bash
# Start dev server
npm run develop

# In another terminal
npm run codegen
```

### IDE Configuration

**VSCode settings** (`.vscode/settings.json`):
```json
{
  "typescript.tsdk": "node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

---

## Migration Checklist

### Setup Phase
- [ ] Install TypeScript and type definitions
- [ ] Create `tsconfig.json`
- [ ] Add `gatsby-plugin-typescript`
- [ ] Create type declaration files
- [ ] Update package.json scripts
- [ ] Configure ESLint for TypeScript
- [ ] Setup GraphQL code generation

### Utilities & Hooks
- [ ] Migrate `config.js` → `config.ts`
- [ ] Migrate `utils/index.js` → `utils/index.ts`
- [ ] Migrate `utils/sr.js` → `utils/sr.ts`
- [ ] Migrate `useScrollDirection`
- [ ] Migrate `usePrefersReducedMotion`
- [ ] Migrate `useOnClickOutside`

### Styles
- [ ] Migrate theme configuration
- [ ] Create theme type definitions
- [ ] Update styled-components types

### Components - Icons (20+ files)
- [ ] Migrate all icon components to `.tsx`

### Components - Core
- [ ] Migrate `head.tsx`
- [ ] Migrate `layout.tsx`
- [ ] Migrate `nav.tsx`
- [ ] Migrate `menu.tsx`
- [ ] Migrate `social.tsx`
- [ ] Migrate `email.tsx`
- [ ] Migrate `footer.tsx`
- [ ] Migrate `loader.tsx`

### Components - Sections
- [ ] Migrate `hero.tsx`
- [ ] Migrate `about.tsx`
- [ ] Migrate `jobs.tsx`
- [ ] Migrate `featured.tsx`
- [ ] Migrate `certs.tsx`
- [ ] Migrate `projects.tsx`
- [ ] Migrate `contact.tsx`

### Pages
- [ ] Migrate `pages/index.tsx`
- [ ] Migrate `pages/404.tsx`
- [ ] Migrate `pages/blog/index.tsx`
- [ ] Migrate `pages/blog/tags.tsx`

### Templates
- [ ] Migrate `templates/post.tsx`
- [ ] Migrate `templates/tag.tsx`

### Gatsby Files - DO NOT MIGRATE
- [ ] ✅ Verify `gatsby-node.js` stays as `.js`
- [ ] ✅ Verify `gatsby-config.js` stays as `.js`
- [ ] ✅ Verify `gatsby-ssr.js` stays as `.js`
- [ ] (Optional) Add JSDoc type annotations to Gatsby files

### Testing & Validation
- [ ] **FIRST**: Run `npm run verify-no-js` (must pass - 0 JS files in src/)
- [ ] Run type check (`npm run type-check`)
- [ ] Build production bundle
- [ ] Test all pages manually
- [ ] Verify GraphQL queries
- [ ] Check bundle size
- [ ] Test responsive design
- [ ] Verify SEO meta tags

### Cleanup
- [ ] Remove PropTypes dependency
- [ ] Delete old `.js` files
- [ ] Update documentation
- [ ] Update README

### Deployment
- [ ] Test build on CI/CD
- [ ] Deploy to staging
- [ ] Test staging thoroughly
- [ ] Deploy to production
- [ ] Monitor for errors

---

## Estimated Timeline

| Phase | Duration | Complexity |
|-------|----------|------------|
| Setup | 2-4 hours | Low |
| Type Definitions | 3-5 hours | Medium |
| Utilities & Hooks | 2-3 hours | Low |
| Icon Components | 2-3 hours | Low |
| Core Components | 5-8 hours | Medium |
| Section Components | 8-12 hours | High |
| Pages & Templates | 4-6 hours | Medium |
| Gatsby Files | 2-3 hours | Medium |
| Testing | 4-6 hours | Medium |
| Cleanup & Docs | 2-3 hours | Low |

**Total: 34-53 hours (approximately 5-7 working days)**

---

## Common Issues & Solutions

### Issue 1: styled-components Type Errors

**Problem**: Theme props not typed correctly

**Solution**:
```typescript
// Ensure DefaultTheme is extended
declare module 'styled-components' {
  export interface DefaultTheme extends Theme {}
}
```

### Issue 2: GraphQL Query Types

**Problem**: GraphQL queries return `any`

**Solution**:
```bash
# Generate types
npm run codegen

# Import generated types
import { JobsQuery } from '../types/graphql';
const data = useStaticQuery<JobsQuery>(graphql`...`);
```

### Issue 3: Ref Types

**Problem**: useRef types incorrect

**Solution**:
```typescript
// For DOM elements
const ref = useRef<HTMLDivElement>(null);

// For mutable values
const ref = useRef<number>(0);
```

### Issue 4: Event Handler Types

**Problem**: Event types unclear

**Solution**:
```typescript
const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
  // ...
};

const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  // ...
};
```

### Issue 5: Window/Document SSR Issues

**Problem**: window is undefined during SSR

**Solution**:
```typescript
if (typeof window !== 'undefined') {
  // Browser-only code
}
```

---

## Benefits After Migration

### Developer Experience
- ✅ IntelliSense/autocomplete in IDE
- ✅ Immediate error detection
- ✅ Refactoring confidence
- ✅ Better documentation (self-documenting code)

### Code Quality
- ✅ Type safety prevents runtime errors
- ✅ GraphQL query validation
- ✅ Consistent prop interfaces
- ✅ Reduced PropTypes boilerplate

### Maintainability
- ✅ Easier onboarding for new developers
- ✅ Clear contracts between components
- ✅ Safer refactoring
- ✅ Better tooling support

---

## Conclusion

This migration plan provides a comprehensive, step-by-step approach to **completely converting** the john-pratt.com portfolio from JavaScript to TypeScript. This is a **100% conversion** - no JavaScript source files will remain (except required config files like `prettier.config.js`).

### Final State
After migration:
- ✅ **0** JavaScript files in `src/` directory
- ✅ **ALL** components in TypeScript (`.tsx`)
- ✅ **ALL** utilities and hooks in TypeScript (`.ts`)
- ✅ **ALL** pages and templates in TypeScript (`.tsx`)
- ⚠️ Gatsby config files remain as JavaScript (`.js`) - gatsby-node.js, gatsby-config.js, gatsby-ssr.js
- ⚠️ Tool config files may remain as JavaScript (`.js`) - prettier.config.js, .eslintrc.js
- ✅ Strict type checking enabled
- ✅ Full type safety across the entire application codebase

### Timeline
The migration should take approximately **2-3 weeks** (34-53 hours) for a thorough, tested conversion. This includes:
- TypeScript setup and configuration
- Creating comprehensive type definitions
- Converting all 30+ components
- Migrating all hooks and utilities
- Converting pages and templates
- Updating Gatsby configuration
- Full testing and validation
- Documentation updates

### Benefits
The resulting codebase will be:
- **Type-safe**: Catch errors at compile time, not runtime
- **Maintainable**: Self-documenting code with clear interfaces
- **Developer-friendly**: Superior IDE support and refactoring capabilities
- **Production-ready**: No compromise, professional TypeScript implementation

**Remember**: This is an all-or-nothing migration. Do not merge until `npm run verify-no-js` passes and all tests succeed. The goal is complete TypeScript adoption, not partial conversion.
