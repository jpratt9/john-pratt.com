import { useState, useEffect, useRef } from 'react';
import usePrefersReducedMotion from './usePrefersReducedMotion';

export const useDelayedMount = (delay: number, condition: boolean = true): boolean => {
  const [isMounted, setIsMounted] = useState(!condition);
  const prefersReducedMotion = usePrefersReducedMotion();
  const hasBeenVisible = useRef(false);

  // Track if content has ever been shown (prevents flash when prefersReducedMotion changes)
  const isCurrentlyVisible = prefersReducedMotion || !condition || isMounted;
  if (isCurrentlyVisible) {
    hasBeenVisible.current = true;
  }

  useEffect(() => {
    if (!condition || prefersReducedMotion) {
      return;
    }

    // If content was already visible (e.g., from SSR with prefersReducedMotion=true),
    // immediately set isMounted to prevent flash when prefersReducedMotion changes
    if (hasBeenVisible.current && !isMounted) {
      setIsMounted(true);
      return;
    }

    if (!isMounted) {
      const timeout = setTimeout(() => setIsMounted(true), delay);
      return () => clearTimeout(timeout);
    }
  }, [condition, prefersReducedMotion, delay, isMounted]);

  // Once visible, stay visible
  return hasBeenVisible.current || isMounted;
};

export default useDelayedMount;
