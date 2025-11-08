import React from 'react';
import { CSSTransition, TransitionGroup } from 'react-transition-group';
import styled from 'styled-components';
import { media } from '@styles';
import { loaderDelay } from '@utils';
import { useDelayedMount, usePrefersReducedMotion } from '@hooks';

interface StyledSideElementProps {
  orientation: string;
}

const StyledSideElement = styled.div<StyledSideElementProps>`
  width: 40px;
  position: fixed;
  bottom: 0;
  left: ${props => (props.orientation === 'left' ? '40px' : 'auto')};
  right: ${props => (props.orientation === 'left' ? 'auto' : '40px')};
  z-index: 10;
  color: var(--light-slate);

  ${media.wide} {
    left: ${props => (props.orientation === 'left' ? '20px' : 'auto')};
    right: ${props => (props.orientation === 'left' ? 'auto' : '20px')};
  }

  ${media.desktop} {
    display: none;
  }
`;

interface SideProps {
  children: React.ReactNode;
  isHome?: boolean;
  orientation: string;
}

const Side: React.FC<SideProps> = ({ children, isHome, orientation }) => {
  const isMounted = useDelayedMount(loaderDelay, isHome || false);
  const prefersReducedMotion = usePrefersReducedMotion();

  return (
    <StyledSideElement orientation={orientation}>
      {prefersReducedMotion ? (
        <>{children}</>
      ) : (
        <TransitionGroup component={null}>
          {isMounted && (
            <CSSTransition classNames={isHome ? 'fade' : ''} timeout={isHome ? loaderDelay : 0}>
              {children}
            </CSSTransition>
          )}
        </TransitionGroup>
      )}
    </StyledSideElement>
  );
};

export default Side;
