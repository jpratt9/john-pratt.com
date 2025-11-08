import { useState, useEffect } from 'react';
import { ScrollDirection, UseScrollDirectionOptions } from '../../types';

const SCROLL_UP: ScrollDirection = 'up';
const SCROLL_DOWN: ScrollDirection = 'down';

const useScrollDirection = (
  options: UseScrollDirectionOptions = {}
): ScrollDirection => {
  const { initialDirection = SCROLL_DOWN, thresholdPixels = 0, off = false } = options;
  const [scrollDir, setScrollDir] = useState<ScrollDirection>(initialDirection);

  useEffect(() => {
    const threshold = thresholdPixels;
    let lastScrollY = window.pageYOffset;
    let ticking = false;

    const updateScrollDir = () => {
      const scrollY = window.pageYOffset;

      if (Math.abs(scrollY - lastScrollY) < threshold) {
        ticking = false;
        return;
      }

      setScrollDir(scrollY > lastScrollY ? SCROLL_DOWN : SCROLL_UP);
      lastScrollY = scrollY > 0 ? scrollY : 0;
      ticking = false;
    };

    const onScroll = () => {
      if (!ticking) {
        window.requestAnimationFrame(updateScrollDir);
        ticking = true;
      }
    };

    if (!off) {
      window.addEventListener('scroll', onScroll);
    } else {
      setScrollDir(initialDirection);
    }

    return () => window.removeEventListener('scroll', onScroll);
  }, [initialDirection, thresholdPixels, off]);

  return scrollDir;
};

export default useScrollDirection;
