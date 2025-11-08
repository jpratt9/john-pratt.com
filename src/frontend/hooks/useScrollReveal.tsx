import { useEffect, RefObject } from 'react';
import { getSr } from '@utils/sr';
import config from '@config';
import usePrefersReducedMotion from './usePrefersReducedMotion';
import { ScrollRevealConfig } from '../../types';

const { srConfig } = config;

export const useScrollReveal = (
  ref: RefObject<HTMLElement | null>,
  customConfig?: ScrollRevealConfig
) => {
  const prefersReducedMotion = usePrefersReducedMotion();

  useEffect(() => {
    if (prefersReducedMotion || !ref.current) return;

    let mounted = true;

    (async () => {
      const sr = await getSr();
      if (!mounted || !sr || !ref.current) return;
      sr.reveal(ref.current, customConfig || srConfig());
    })();

    return () => {
      mounted = false;
    };
  }, [prefersReducedMotion, ref, customConfig]);
};

export const useScrollRevealMultiple = (
  refs: RefObject<(HTMLElement | null)[]>,
  configFn?: (index: number) => ScrollRevealConfig
) => {
  const prefersReducedMotion = usePrefersReducedMotion();

  useEffect(() => {
    if (prefersReducedMotion || !refs.current) return;

    let mounted = true;

    (async () => {
      const sr = await getSr();
      if (!mounted || !sr || !refs.current) return;

      refs.current.forEach((ref, i) => {
        if (ref) {
          const cfg = configFn ? configFn(i) : srConfig(i * 100);
          sr.reveal(ref, cfg);
        }
      });
    })();

    return () => {
      mounted = false;
    };
  }, [prefersReducedMotion, refs, configFn]);
};
