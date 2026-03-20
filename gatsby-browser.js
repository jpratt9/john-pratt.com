/*
 * Implement Gatsby's Browser APIs in this file.
 *
 * See: https://www.gatsbyjs.org/docs/browser-apis/
 */

exports.onRouteUpdate = ({ location }) => {
  if (location.hash) {
    const scrollToHash = () => {
      const el = document.querySelector(location.hash);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      } else {
        requestAnimationFrame(scrollToHash);
      }
    };
    setTimeout(scrollToHash, 100);
  }
};

exports.shouldUpdateScroll = ({ routerProps: { location } }) => {
  if (location.hash) {
    return false;
  }
  return true;
};
