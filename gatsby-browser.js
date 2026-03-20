/*
 * Implement Gatsby's Browser APIs in this file.
 *
 * See: https://www.gatsbyjs.org/docs/browser-apis/
 */

exports.onRouteUpdate = ({ location }) => {
  if (location.hash) {
    const id = location.hash.substring(1);
    const interval = setInterval(() => {
      const el = document.getElementById(id);
      if (el) {
        clearInterval(interval);
        // Use instant scroll to avoid smooth scroll being cancelled by layout shifts
        window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY, behavior: 'instant' });
      }
    }, 200);
    // Give up after 10s
    setTimeout(() => clearInterval(interval), 10000);
  }
};

exports.shouldUpdateScroll = ({ routerProps: { location } }) => {
  if (location.hash) {
    return false;
  }
  return true;
};
