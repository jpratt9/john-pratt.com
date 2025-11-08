import { css, RuleSet } from 'styled-components';

const createButton = (
  padding = '1.25rem 1.75rem',
  fontSize = 'var(--fz-xs)',
  shadowSize = '4px',
  translateSize = '-5px'
) => css`
  color: var(--green);
  background-color: transparent;
  border: 1px solid var(--green);
  border-radius: var(--border-radius);
  font-size: ${fontSize};
  font-family: var(--font-mono);
  line-height: 1;
  text-decoration: none;
  padding: ${padding};
  transition: var(--transition);

  &:hover,
  &:focus-visible {
    outline: none;
    box-shadow: ${shadowSize} ${shadowSize} 0 0 var(--green);
    transform: translate(${translateSize}, ${translateSize});
  }
  &:after {
    display: none !important;
  }
`;

const button = createButton();

const mixins: {
  flexCenter: RuleSet;
  flexBetween: RuleSet;
  link: RuleSet;
  inlineLink: RuleSet;
  button: RuleSet;
  smallButton: RuleSet;
  bigButton: RuleSet;
  boxShadow: RuleSet;
  fancyList: RuleSet;
  resetList: RuleSet;
  verticalLine: RuleSet;
} = {
  flexCenter: css`
    display: flex;
    justify-content: center;
    align-items: center;
  `,

  flexBetween: css`
    display: flex;
    justify-content: space-between;
    align-items: center;
  `,

  link: css`
    display: inline-block;
    text-decoration: none;
    text-decoration-skip-ink: auto;
    color: inherit;
    position: relative;
    transition: var(--transition);

    &:hover,
    &:focus-visible {
      color: var(--green);
      outline: 0;
    }
  `,

  inlineLink: css`
    display: inline-block;
    position: relative;
    color: var(--green);
    transition: var(--transition);

    &:hover,
    &:focus-visible {
      color: var(--green);
      outline: 0;
      &:after {
        width: 100%;
      }
      & > * {
        color: var(--green) !important;
        transition: var(--transition);
      }
    }
    &:after {
      content: '';
      display: block;
      width: 0;
      height: 1px;
      position: relative;
      bottom: 0.37em;
      background-color: var(--green);
      opacity: 0.5;
      @media (prefers-reduced-motion: no-preference) {
        transition: var(--transition);
      }
    }
  `,

  button,

  smallButton: createButton('0.75rem 1rem', 'var(--fz-xs)', '3px', '-4px'),

  bigButton: createButton('1.25rem 1.75rem', 'var(--fz-sm)', '4px', '-5px'),

  boxShadow: css`
    box-shadow: 0 10px 30px -15px var(--navy-shadow);
    transition: var(--transition);

    &:hover,
    &:focus-visible {
      box-shadow: 0 20px 30px -15px var(--navy-shadow);
    }
  `,

  fancyList: css`
    padding: 0;
    margin: 0;
    list-style: none;
    font-size: var(--fz-lg);
    li {
      position: relative;
      padding-left: 30px;
      margin-bottom: 10px;
      &:before {
        content: '▹';
        position: absolute;
        left: 0;
        color: var(--green);
      }
    }
  `,

  resetList: css`
    list-style: none;
    padding: 0;
    margin: 0;
  `,

  verticalLine: css`
    &:after {
      content: '';
      display: block;
      width: 1px;
      height: 90px;
      margin: 0 auto;
      background-color: var(--light-slate);
    }
  `,
};

export default mixins;
