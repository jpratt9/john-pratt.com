/*
 * https://www.joshwcomeau.com/snippets/react-hooks/use-prefers-reduced-motion/
 */

import { useState, useEffect } from 'react';

const QUERY = '(prefers-reduced-motion: no-preference)';

function usePrefersReducedMotion(): boolean {
  // Always start with true (assumes reduced motion) for consistent SSR/client hydration.
  // This prevents hydration mismatch where server renders one branch and client renders another.
  // The actual preference is checked in useEffect after hydration completes.
  const [prefersReducedMotion, setPrefersReducedMotion] = useState<boolean>(true);

  useEffect(() => {
    const mediaQueryList = window.matchMedia(QUERY);

    // Set actual preference after hydration
    setPrefersReducedMotion(!mediaQueryList.matches);

    const listener = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(!event.matches);
    };

    // Use addEventListener for modern browsers, fallback to addListener
    if (mediaQueryList.addEventListener) {
      mediaQueryList.addEventListener('change', listener);
    } else {
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
}

export default usePrefersReducedMotion;
