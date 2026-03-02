import React, { useState, useEffect } from 'react';
import { createTimeline, svg } from 'animejs';
import styled from 'styled-components';
import { IconLoader } from '@components/icons';

interface StyledLoaderProps {
  isMounted: boolean;
}

const StyledLoader = styled.div<StyledLoaderProps>`
  ${({ theme }) => theme.mixins.flexCenter};
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
  width: 100%;
  height: 100%;
  background-color: var(--dark-navy);
  z-index: 99;

  .logo-wrapper {
    width: max-content;
    max-width: 100px;
    transition: var(--transition);
    opacity: ${props => (props.isMounted ? 1 : 0)};
    svg {
      display: block;
      width: 100%;
      height: 100%;
      margin: 0 auto;
      fill: none;
      user-select: none;
      #B {
        opacity: 0;
      }
    }
  }
`;

interface LoaderProps {
  finishLoading: () => void;
}

const Loader: React.FC<LoaderProps> = ({ finishLoading }) => {
  const [isMounted, setIsMounted] = useState(false);

  const animateLogo = () => {
    const loader = createTimeline({
      onComplete: () => finishLoading(),
    });

    // 1) draw the logo paths (v4 "draw" replaces setDashoffset)
    loader.add(svg.createDrawable('#logo path'), {
      delay: 210,
      duration: 1050,
      ease: 'inOutQuart',
      draw: '0 1',
    });

    // 2) fade in the "B"
    loader.add('#logo #B', {
      duration: 490,
      ease: 'inOutQuart',
      opacity: 1,
    });

    // 3) fade + scale out logo
    loader.add('#logo', {
      delay: 350,
      duration: 210,
      ease: 'inOutQuart',
      opacity: 0,
      scale: 0.1,
    });

    // 4) hide the loader container
    loader.add('.loader', {
      duration: 140,
      ease: 'inOutQuart',
      opacity: 0,
      zIndex: -1,
    });
  };

  useEffect(() => {
    document.body.classList.add('hidden');
    const timeout = setTimeout(() => setIsMounted(true), 10);
    return () => {
      clearTimeout(timeout);
      document.body.classList.remove('hidden');
    };
  }, []);

  // Start the animation once mounted (ensures DOM is ready)
  useEffect(() => {
    if (isMounted) animateLogo();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isMounted]);

  return (
    <StyledLoader className="loader" isMounted={isMounted}>
      <div className="logo-wrapper">
        <IconLoader />
      </div>
    </StyledLoader>
  );
};

export default Loader;
