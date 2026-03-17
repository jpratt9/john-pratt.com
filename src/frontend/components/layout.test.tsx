import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, act } from '@testing-library/react';
import React from 'react';
import Layout from './layout';

// Mock child components to isolate layout logic
vi.mock('./nav', () => ({ default: ({ isHome }: any) => <div data-testid="nav" data-is-home={isHome} /> }));
vi.mock('./social', () => ({ default: ({ isHome }: any) => <div data-testid="social" data-is-home={isHome} /> }));
vi.mock('./email', () => ({ default: ({ isHome }: any) => <div data-testid="email" data-is-home={isHome} /> }));
vi.mock('./footer', () => ({ default: () => <div data-testid="footer" /> }));
let mockFinishLoading: (() => void) | null = null;
vi.mock('./loader', () => ({
  default: ({ finishLoading }: { finishLoading: () => void }) => {
    mockFinishLoading = finishLoading;
    return <div data-testid="loader" />;
  },
}));

const mockLocation = (pathname: string, hash = '') => ({
  pathname,
  hash,
  search: '',
  href: `http://localhost${pathname}${hash}`,
  origin: 'http://localhost',
  protocol: 'http:',
  host: 'localhost',
  hostname: 'localhost',
  port: '',
  state: null,
  key: '',
});

describe('Layout', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
    document.body.classList.remove('hidden');
    mockFinishLoading = null;
  });

  describe('loader / sessionStorage behavior', () => {
    it('shows loader on first visit to homepage', async () => {
      render(
        <Layout location={mockLocation('/')}>
          <div data-testid="content">Home</div>
        </Layout>,
      );

      // Loader is lazy-loaded via Suspense, wait for it
      const loader = await screen.findByTestId('loader');
      expect(loader).toBeTruthy();
      expect(screen.queryByTestId('content')).toBeNull();
    });

    it('sets sessionStorage hasLoaded after loader finishes', async () => {
      expect(sessionStorage.getItem('hasLoaded')).toBeNull();

      render(
        <Layout location={mockLocation('/')}>
          <div data-testid="content">Home</div>
        </Layout>,
      );

      await screen.findByTestId('loader');

      await act(async () => {
        mockFinishLoading?.();
      });

      expect(sessionStorage.getItem('hasLoaded')).toBe('1');
    });

    it('skips loader on homepage when hasLoaded is set', () => {
      sessionStorage.setItem('hasLoaded', '1');

      render(
        <Layout location={mockLocation('/')}>
          <div data-testid="content">Home</div>
        </Layout>,
      );

      expect(screen.queryByTestId('loader')).toBeNull();
      expect(screen.getByTestId('content')).toBeTruthy();
    });

    it('renders content immediately after loader finishes', async () => {
      render(
        <Layout location={mockLocation('/')}>
          <div data-testid="content">Home</div>
        </Layout>,
      );

      await screen.findByTestId('loader');
      expect(screen.queryByTestId('content')).toBeNull();

      await act(async () => {
        mockFinishLoading?.();
      });

      expect(screen.getByTestId('content')).toBeTruthy();
      expect(screen.getByTestId('nav')).toBeTruthy();
    });

    it('never shows loader on non-home pages', () => {
      render(
        <Layout location={mockLocation('/blog')}>
          <div data-testid="content">Blog</div>
        </Layout>,
      );

      expect(screen.queryByTestId('loader')).toBeNull();
      expect(screen.getByTestId('content')).toBeTruthy();
    });

    it('never shows loader on /contact', () => {
      render(
        <Layout location={mockLocation('/contact')}>
          <div data-testid="content">Contact</div>
        </Layout>,
      );

      expect(screen.queryByTestId('loader')).toBeNull();
      expect(screen.getByTestId('content')).toBeTruthy();
    });

    it('skips loader when navigating from /blog to / after initial load', async () => {
      // Simulate first visit completing
      sessionStorage.setItem('hasLoaded', '1');

      // Navigate to homepage
      render(
        <Layout location={mockLocation('/')}>
          <div data-testid="content">Home</div>
        </Layout>,
      );

      expect(screen.queryByTestId('loader')).toBeNull();
      expect(screen.getByTestId('content')).toBeTruthy();
    });

    it('skips loader when navigating to /#jobs after initial load', () => {
      sessionStorage.setItem('hasLoaded', '1');

      render(
        <Layout location={mockLocation('/', '#jobs')}>
          <div data-testid="content">Home</div>
        </Layout>,
      );

      expect(screen.queryByTestId('loader')).toBeNull();
      expect(screen.getByTestId('content')).toBeTruthy();
    });

    it('skips loader when navigating to /#projects after initial load', () => {
      sessionStorage.setItem('hasLoaded', '1');

      render(
        <Layout location={mockLocation('/', '#projects')}>
          <div data-testid="content">Home</div>
        </Layout>,
      );

      expect(screen.queryByTestId('loader')).toBeNull();
      expect(screen.getByTestId('content')).toBeTruthy();
    });

    it('shows loader on fresh session even if previously visited', async () => {
      // No sessionStorage set = fresh session
      render(
        <Layout location={mockLocation('/')}>
          <div data-testid="content">Home</div>
        </Layout>,
      );

      expect(await screen.findByTestId('loader')).toBeTruthy();
    });
  });

  describe('isHome detection', () => {
    it('passes isHome=true to nav/social/email on homepage', async () => {
      sessionStorage.setItem('hasLoaded', '1');

      render(
        <Layout location={mockLocation('/')}>
          <div>Home</div>
        </Layout>,
      );

      expect(screen.getByTestId('nav').getAttribute('data-is-home')).toBe('true');
      expect(screen.getByTestId('social').getAttribute('data-is-home')).toBe('true');
      expect(screen.getByTestId('email').getAttribute('data-is-home')).toBe('true');
    });

    it('passes isHome=false to nav/social/email on other pages', () => {
      render(
        <Layout location={mockLocation('/blog')}>
          <div>Blog</div>
        </Layout>,
      );

      expect(screen.getByTestId('nav').getAttribute('data-is-home')).toBe('false');
      expect(screen.getByTestId('social').getAttribute('data-is-home')).toBe('false');
      expect(screen.getByTestId('email').getAttribute('data-is-home')).toBe('false');
    });
  });

  describe('hash navigation', () => {
    it('scrolls to element matching location hash', async () => {
      sessionStorage.setItem('hasLoaded', '1');

      const mockElement = document.createElement('div');
      mockElement.id = 'jobs';
      mockElement.focus = vi.fn();
      document.body.appendChild(mockElement);

      render(
        <Layout location={mockLocation('/', '#jobs')}>
          <div>Home</div>
        </Layout>,
      );

      await act(async () => {
        await new Promise(r => setTimeout(r, 10));
      });

      expect(mockElement.scrollIntoView).toHaveBeenCalledWith({
        behavior: 'smooth',
        block: 'start',
      });
      expect(mockElement.focus).toHaveBeenCalled();

      document.body.removeChild(mockElement);
    });
  });

  describe('external links', () => {
    it('sets target and rel on external links', async () => {
      sessionStorage.setItem('hasLoaded', '1');

      render(
        <Layout location={mockLocation('/blog')}>
          <a href="https://external.com" data-testid="ext-link">External</a>
        </Layout>,
      );

      await act(async () => {
        await new Promise(r => setTimeout(r, 10));
      });

      const link = screen.getByTestId('ext-link');
      expect(link.getAttribute('target')).toBe('_blank');
      expect(link.getAttribute('rel')).toBe('noopener noreferrer');
    });

    it('does not modify internal links', async () => {
      sessionStorage.setItem('hasLoaded', '1');

      render(
        <Layout location={mockLocation('/blog')}>
          <a href="/contact" data-testid="int-link">Contact</a>
        </Layout>,
      );

      await act(async () => {
        await new Promise(r => setTimeout(r, 10));
      });

      const link = screen.getByTestId('int-link');
      expect(link.getAttribute('target')).toBeNull();
    });
  });
});
