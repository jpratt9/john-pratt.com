import { useState, useEffect } from 'react';
import usePrefersReducedMotion from './usePrefersReducedMotion';

export const useDelayedMount = (delay: number, condition: boolean = true): boolean => {
  const [isMounted, setIsMounted] = useState(!condition);
  const prefersReducedMotion = usePrefersReducedMotion();

  useEffect(() => {
    if (!condition || prefersReducedMotion) {
      return;
    }

    const timeout = setTimeout(() => setIsMounted(true), delay);
    return () => clearTimeout(timeout);
  }, [condition, prefersReducedMotion, delay]);

  return prefersReducedMotion || !condition ? true : isMounted;
};

export default useDelayedMount;
