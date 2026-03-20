/*
 * Implement Gatsby's Browser APIs in this file.
 *
 * See: https://www.gatsbyjs.org/docs/browser-apis/
 */

// Log all sessionStorage scroll keys on load
exports.onClientEntry = () => {
  console.log('[SCROLL DEBUG] onClientEntry fired');
  console.log('[SCROLL DEBUG] window.scrollY at entry:', window.scrollY);
  for (let i = 0; i < sessionStorage.length; i++) {
    const key = sessionStorage.key(i);
    if (key.startsWith('@@scroll')) {
      console.log(`[SCROLL DEBUG] sessionStorage: ${key} =`, sessionStorage.getItem(key));
    }
  }

  // Monitor all scroll events
  let scrollCount = 0;
  window.addEventListener('scroll', () => {
    scrollCount++;
    if (scrollCount <= 20) {
      console.log(`[SCROLL DEBUG] scroll event #${scrollCount}, scrollY: ${window.scrollY}`, new Error().stack?.split('\n').slice(1, 4).join(' <- '));
    }
  });

  // Monitor scrollTo calls
  const origScrollTo = window.scrollTo.bind(window);
  window.scrollTo = (...args) => {
    console.log('[SCROLL DEBUG] window.scrollTo called with:', args, new Error().stack?.split('\n').slice(1, 5).join(' <- '));
    return origScrollTo(...args);
  };
};

exports.onInitialClientRender = () => {
  console.log('[SCROLL DEBUG] onInitialClientRender fired, scrollY:', window.scrollY);
};

exports.onRouteUpdate = ({ location }) => {
  console.log('[SCROLL DEBUG] onRouteUpdate fired', { hash: location.hash, pathname: location.pathname, scrollY: window.scrollY });
  if (location.hash) {
    const id = location.hash.substring(1);
    let tick = 0;
    const interval = setInterval(() => {
      tick++;
      const el = document.getElementById(id);
      console.log(`[SCROLL DEBUG] poll tick ${tick}, element #${id}:`, el ? `FOUND (offsetTop: ${el.offsetTop})` : 'NOT FOUND', 'scrollY:', window.scrollY);
      if (el) {
        clearInterval(interval);
        const top = el.getBoundingClientRect().top + window.scrollY;
        console.log(`[SCROLL DEBUG] scrolling to ${top}`);
        window.scrollTo({ top, behavior: 'instant' });
        setTimeout(() => {
          console.log(`[SCROLL DEBUG] after scroll, scrollY:`, window.scrollY);
        }, 100);
      }
    }, 200);
    setTimeout(() => { clearInterval(interval); console.log('[SCROLL DEBUG] gave up after 10s'); }, 10000);
  }
};

exports.shouldUpdateScroll = ({ prevRouterProps, routerProps: { location }, getSavedScrollPosition }) => {
  const saved = getSavedScrollPosition(location);
  console.log('[SCROLL DEBUG] shouldUpdateScroll called', { hash: location.hash, pathname: location.pathname, savedPosition: saved, scrollY: window.scrollY });
  if (location.hash) {
    console.log('[SCROLL DEBUG] returning false (has hash)');
    return false;
  }
  return true;
};
