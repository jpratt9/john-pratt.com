import React, { useState, useEffect, useRef, ReactNode } from 'react';
import { CSSTransition } from 'react-transition-group';
import styled from 'styled-components';
import { media } from '@styles';
import { KEY_CODES } from '@utils';

interface TabItem {
  label: string;
  content: ReactNode;
}

interface TabNavigationProps {
  tabs: TabItem[];
  ariaLabel: string;
}

interface StyledTabButtonProps {
  isActive: boolean;
}

interface StyledHighlightProps {
  activeTabId: number;
}

const StyledTabList = styled.div`
  position: relative;
  z-index: 3;
  width: max-content;
  padding: 0;
  margin: 0;
  list-style: none;

  ${media.tablet} {
    display: flex;
    overflow-x: auto;
    width: calc(100% + 100px);
    padding-left: 50px;
    margin-left: -50px;
    margin-bottom: 30px;
  }
  ${media.mobile} {
    width: calc(100% + 50px);
    padding-left: 25px;
    margin-left: -25px;
  }

  li {
    &:first-of-type {
      ${media.tablet} {
        margin-left: 50px;
      }
      ${media.mobile} {
        margin-left: 25px;
      }
    }
    &:last-of-type {
      ${media.tablet} {
        padding-right: 50px;
      }
      ${media.mobile} {
        padding-right: 25px;
      }
    }
  }
`;

const StyledTabButton = styled.button<StyledTabButtonProps>`
  ${({ theme }) => theme.mixins.link};
  display: flex;
  align-items: center;
  width: 100%;
  height: var(--tab-height);
  padding: 0 20px 2px;
  border-left: 2px solid var(--lightest-navy);
  background-color: transparent;
  color: ${({ isActive }) => (isActive ? 'var(--green)' : 'var(--slate)')};
  font-family: var(--font-mono);
  font-size: var(--fz-xs);
  text-align: left;
  white-space: nowrap;

  ${media.desktop} {
    padding: 0 15px 2px;
  }
  ${media.tablet} {
    ${({ theme }) => theme.mixins.flexCenter};
    min-width: 120px;
    padding: 0 15px;
    border-left: 0;
    border-bottom: 2px solid var(--lightest-navy);
    text-align: center;
  }

  &:hover,
  &:focus {
    background-color: var(--light-navy);
  }
`;

const StyledHighlight = styled.div<StyledHighlightProps>`
  position: absolute;
  top: 0;
  left: 0;
  z-index: 10;
  width: 2px;
  height: var(--tab-height);
  border-radius: var(--border-radius);
  background: var(--green);
  transform: translateY(calc(${({ activeTabId }) => activeTabId} * var(--tab-height)));
  transition: transform 0.25s cubic-bezier(0.645, 0.045, 0.355, 1);
  transition-delay: 0.1s;

  ${media.tablet} {
    top: auto;
    bottom: 0;
    width: 100%;
    max-width: var(--tab-width);
    height: 2px;
    margin-left: 50px;
    transform: translateX(calc(${({ activeTabId }) => activeTabId} * var(--tab-width)));
  }
  ${media.mobile} {
    margin-left: 25px;
  }
`;

const StyledTabPanels = styled.div`
  position: relative;
  width: 100%;
  margin-left: 20px;

  ${media.tablet} {
    margin-left: 0;
  }
`;

const StyledTabPanel = styled.div`
  width: 100%;
  height: auto;
  padding: 10px 5px;
`;

const StyledInner = styled.div`
  display: flex;

  ${media.tablet} {
    display: block;
  }

  @media (min-width: 700px) {
    min-height: 340px;
  }
`;

export const TabNavigation: React.FC<TabNavigationProps> = ({ tabs, ariaLabel }) => {
  const [activeTabId, setActiveTabId] = useState(0);
  const [tabFocus, setTabFocus] = useState<number | null>(null);
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);

  const focusTab = () => {
    if (tabFocus !== null && tabRefs.current[tabFocus]) {
      tabRefs.current[tabFocus]?.focus();
      return;
    }
    if (tabFocus !== null && tabFocus >= tabRefs.current.length) {
      setTabFocus(0);
    }
    if (tabFocus !== null && tabFocus < 0) {
      setTabFocus(tabRefs.current.length - 1);
    }
  };

  useEffect(() => focusTab(), [tabFocus]);

  const onKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case KEY_CODES.ARROW_UP:
        e.preventDefault();
        setTabFocus(tabFocus !== null ? tabFocus - 1 : 0);
        break;
      case KEY_CODES.ARROW_DOWN:
        e.preventDefault();
        setTabFocus(tabFocus !== null ? tabFocus + 1 : 0);
        break;
      default:
        break;
    }
  };

  return (
    <StyledInner>
      <StyledTabList role="tablist" aria-label={ariaLabel} onKeyDown={onKeyDown}>
        {tabs.map((tab, i) => (
          <StyledTabButton
            key={i}
            isActive={activeTabId === i}
            onClick={() => setActiveTabId(i)}
            ref={el => {
              tabRefs.current[i] = el;
            }}
            id={`tab-${i}`}
            role="tab"
            tabIndex={activeTabId === i ? 0 : -1}
            aria-selected={activeTabId === i}
            aria-controls={`panel-${i}`}
          >
            <span>{tab.label}</span>
          </StyledTabButton>
        ))}
        <StyledHighlight activeTabId={activeTabId} />
      </StyledTabList>

      <StyledTabPanels>
        {tabs.map((tab, i) => (
          <CSSTransition key={i} in={activeTabId === i} timeout={250} classNames="fade">
            <StyledTabPanel
              id={`panel-${i}`}
              role="tabpanel"
              tabIndex={activeTabId === i ? 0 : -1}
              aria-labelledby={`tab-${i}`}
              aria-hidden={activeTabId !== i}
              hidden={activeTabId !== i}
            >
              {tab.content}
            </StyledTabPanel>
          </CSSTransition>
        ))}
      </StyledTabPanels>
    </StyledInner>
  );
};

export default TabNavigation;
