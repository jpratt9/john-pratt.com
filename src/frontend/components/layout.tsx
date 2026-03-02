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
