import 'styled-components';
import { RuleSet } from 'styled-components';

declare module 'styled-components' {
  export interface DefaultTheme {
    bp: {
      mobileS: string;
      mobileM: string;
      mobileL: string;
      tabletS: string;
      tabletL: string;
      desktopXS: string;
      desktopS: string;
      desktopM: string;
      desktopL: string;
    };
    mixins: {
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
    };
  }
}
