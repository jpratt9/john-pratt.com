/*
 * Implement Gatsby's Browser APIs in this file.
 *
 * See: https://www.gatsbyjs.org/docs/browser-apis/
 */

exports.onRouteUpdate = ({ location }) => {
  console.log('[SCROLL DEBUG] onRouteUpdate fired', { hash: location.hash, pathname: location.pathname });
  if (location.hash) {
    const id = location.hash.substring(1);
    let tick = 0;
    const interval = setInterval(() => {
      tick++;
      const el = document.getElementById(id);
      console.log(`[SCROLL DEBUG] poll tick ${tick}, element #${id}:`, el ? 'FOUND' : 'NOT FOUND');
      if (el) {
        clearInterval(interval);
        const top = el.getBoundingClientRect().top + window.scrollY;
        console.log(`[SCROLL DEBUG] scrolling to ${top}`);
        window.scrollTo({ top, behavior: 'instant' });
        setTimeout(() => {
          console.log(`[SCROLL DEBUG] after scroll, window.scrollY =`, window.scrollY);
        }, 100);
      }
    }, 200);
    setTimeout(() => { clearInterval(interval); console.log('[SCROLL DEBUG] gave up after 10s'); }, 10000);
  }
};

exports.shouldUpdateScroll = ({ routerProps: { location } }) => {
  console.log('[SCROLL DEBUG] shouldUpdateScroll called', { hash: location.hash });
  if (location.hash) {
    console.log('[SCROLL DEBUG] returning false (blocking Gatsby scroll)');
    return false;
  }
  return true;
};
