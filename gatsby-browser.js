/*
 * Implement Gatsby's Browser APIs in this file.
 *
 * See: https://www.gatsbyjs.org/docs/browser-apis/
 */

exports.shouldUpdateScroll = ({ routerProps: { location } }) => {
  if (location.hash) {
    // Let the browser handle hash scrolling natively
    window.setTimeout(() => {
      const el = document.querySelector(location.hash);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }, 800);
    return false;
  }
  return true;
};
