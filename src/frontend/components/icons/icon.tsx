import React from 'react';
import {
  IconAppStore,
  IconBookmark,
  IconCodepen,
  IconExternal,
  IconFolder,
  IconFork,
  IconGitHub,
  //   IconCalendly,
  IconInstagram,
  IconLinkedin,
  IconLoader,
  IconLogo,
  IconPlayStore,
  IconStar,
} from '@components/icons';

export type IconName =
  | 'AppStore'
  | 'Bookmark'
  | 'Codepen'
  | 'External'
  | 'Folder'
  | 'Fork'
  | 'GitHub'
  | 'Instagram'
  | 'Linkedin'
  | 'Loader'
  | 'Logo'
  | 'PlayStore'
  | 'Star';

interface IconProps {
  name: IconName;
}

const Icon: React.FC<IconProps> = ({ name }) => {
  switch (name) {
    case 'AppStore':
      return <IconAppStore />;
    case 'Bookmark':
      return <IconBookmark />;
    case 'Codepen':
      return <IconCodepen />;
    case 'External':
      return <IconExternal />;
    case 'Folder':
      return <IconFolder />;
    case 'Fork':
      return <IconFork />;
    case 'GitHub':
      return <IconGitHub />;
    // case 'Calendly':
    //     return <IconCalendly />
    case 'Instagram':
      return <IconInstagram />;
    case 'Linkedin':
      return <IconLinkedin />;
    case 'Loader':
      return <IconLoader />;
    case 'Logo':
      return <IconLogo />;
    case 'PlayStore':
      return <IconPlayStore />;
    case 'Star':
      return <IconStar />;
    default:
      return <IconExternal />;
  }
};

export default Icon;
