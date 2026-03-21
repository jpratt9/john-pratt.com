import React, { useState, useEffect } from 'react';
import styled, { ThemeProvider } from 'styled-components';
import { Loader, Nav, Social, Email, Footer } from '@components';
import { GlobalStyle, theme } from '@styles';
import { Location } from '../../types';

const StyledContent = styled.div`
  display: flex;
  flex-direction: column;
  min-height: 100vh;
`;

interface LayoutProps {
  children: React.ReactNode;
  location: Location;
}

// =============================================================================
// WARNING: THIS COMPONENT HAS EXTREMELY FRAGILE LOADING/HYDRATION LOGIC.
// DO NOT MODIFY the loader state management without reading these comments.
// We spent hours debugging a production-only bug caused by hydration mismatches.
// =============================================================================
//
// HOW IT WORKS:
// - On the homepage, a logo animation (Loader) plays on the FIRST visit per tab.
// - After the Loader finishes, we set sessionStorage('hasLoaded') so subsequent
//   refreshes skip the animation and go straight to content.
//
// WHY useState(isHome) AND NOT useState(isHome && !hasLoaded):
// - Gatsby pre-renders pages on the server (SSR). The server has NO sessionStorage,
//   so it always renders the Loader for the homepage.
// - If the client reads sessionStorage during useState initialization and decides
//   to skip the Loader, the client's initial render (Content) won't match the
//   server's render (Loader). React calls this a "hydration mismatch."
// - A hydration mismatch causes React to THROW AWAY the server HTML and re-render
//   from scratch. This completely breaks the page — the background disappears,
//   you land in the middle of the page, and scrolling stops working.
// - To avoid this, we ALWAYS start with isLoading=true on the homepage (matching
//   the server), and then IMMEDIATELY skip the Loader in a useEffect (which only
//   runs on the client, after hydration is complete). This way:
//     1. Server renders Loader HTML
//     2. Client hydrates Loader HTML (matches! no mismatch!)
//     3. useEffect fires → checks sessionStorage → setIsLoading(false) → shows content
//   The Loader may flash for a single frame on return visits, but the page won't break.
//
// DO NOT:
// - Move the sessionStorage check back into useState — it WILL break production.
// - Wrap the Loader in React.lazy/Suspense — it causes similar hydration issues.
// - Add scroll handling to gatsby-browser.js — layout.tsx handles it (see below).
// - Remove the Loader entirely — the hash scroll logic depends on the isLoading
//   state to know when content is ready in the DOM.
// =============================================================================

const Layout: React.FC<LayoutProps> = ({ children, location }) => {
  const isHome = location.pathname === '/';

  // MUST start as isHome (not isHome && !hasLoaded) to match SSR. See warning above.
  const [isLoading, setIsLoading] = useState(isHome);

  // Skip loader on return visits. MUST be in useEffect (not useState) to avoid
  // hydration mismatch. See the giant warning comment above for why.
  useEffect(() => {
    if (isHome && sessionStorage.getItem('hasLoaded')) {
      setIsLoading(false);
    }
  }, []);

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

  // After loading finishes (either Loader animation completes or sessionStorage
  // skip fires), scroll to hash target if present and set up external links.
  useEffect(() => {
    if (isLoading) {
      return;
    }

    if (location.hash) {
      const id = location.hash.substring(1);
      setTimeout(() => {
        const el = document.getElementById(id);
        if (el) {
          el.scrollIntoView();
          el.focus();
        }
      }, 0);
    }

    handleExternalLinks();
  }, [isLoading]);

  return (
    <>
      <div id="root">
        <ThemeProvider theme={theme}>
          <GlobalStyle />

          <a className="skip-to-content" href="#content">
            Skip to Content
          </a>

          {/* Loader shows on first homepage visit. finishLoading sets sessionStorage
              so it won't show again in this tab. See warning comment above. */}
          {isLoading && isHome ? (
            <Loader finishLoading={() => { sessionStorage.setItem('hasLoaded', '1'); setIsLoading(false); }} />
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
