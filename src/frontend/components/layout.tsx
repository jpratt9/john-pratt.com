import React, { useState, useEffect, lazy, Suspense } from 'react';
import styled, { ThemeProvider } from 'styled-components';
import { Nav, Social, Email, Footer } from '@components';
import { GlobalStyle, theme } from '@styles';
import { Location } from '../../types';

const Loader = lazy(() => import('./loader' /* webpackChunkName: "loader" */));

const StyledContent = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
`;

interface LayoutProps {
  children: React.ReactNode;
  location: Location;
}

const Layout: React.FC<LayoutProps> = ({ children, location }) => {
  const isHome = location.pathname === '/';
  const hasLoaded = typeof window !== 'undefined' && sessionStorage.getItem('hasLoaded');
  const [isLoading, setIsLoading] = useState(isHome && !hasLoaded);

  // Sets target="_blank" rel="noopener noreferrer" on external links
  const handleExternalLinks = () => {
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
    console.log('[SCROLL DEBUG layout] useEffect fired, isLoading:', isLoading, 'hash:', location.hash);
    if (isLoading) return;

    handleExternalLinks();

    if (location.hash) {
      const id = location.hash.substring(1);
      let tick = 0;
      const interval = setInterval(() => {
        tick++;
        const el = document.getElementById(id);
        console.log(`[SCROLL DEBUG layout] poll tick ${tick}, element #${id}:`, el ? 'FOUND' : 'NOT FOUND');
        if (el) {
          clearInterval(interval);
          const top = el.getBoundingClientRect().top + window.scrollY;
          console.log(`[SCROLL DEBUG layout] scrolling to ${top}`);
          window.scrollTo({ top, behavior: 'instant' });
          setTimeout(() => {
            console.log(`[SCROLL DEBUG layout] after scroll, window.scrollY =`, window.scrollY);
          }, 100);
        }
      }, 200);
      setTimeout(() => clearInterval(interval), 10000);
    }
  }, [isLoading]);

  return (
    <>
      <div id="root">
        <ThemeProvider theme={theme}>
          <GlobalStyle />

          <a className="skip-to-content" href="#content">
            Skip to Content
          </a>

          {isLoading && isHome ? (
            <Suspense fallback={null}>
              <Loader finishLoading={() => { sessionStorage.setItem('hasLoaded', '1'); setIsLoading(false); }} />
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
