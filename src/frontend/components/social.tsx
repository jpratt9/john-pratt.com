import React from 'react';
import { Link } from 'gatsby';
import styled from 'styled-components';
import config from '@config';
import { Side } from '@components';
import { Icon, IconName } from '@components/icons';
import { IconEnvelope } from '@components/icons';

const { socialMedia } = config;

const StyledSocialList = styled.ul`
  display: flex;
  flex-direction: column;
  align-items: center;
  margin: 0;
  padding: 0;
  list-style: none;
  ${({ theme }) => theme.mixins.verticalLine};

  li {
    &:last-of-type {
      margin-bottom: 20px;
    }

    a {
      padding: 10px;

      &:hover,
      &:focus {
        transform: translateY(-3px);
      }

      svg {
        width: 20px;
        height: 20px;
      }
    }
  }
`;

interface SocialProps {
  isHome?: boolean;
}

const Social: React.FC<SocialProps> = ({ isHome }) => (
  <Side isHome={isHome} orientation="left">
    <StyledSocialList>
      {socialMedia &&
        socialMedia.map(({ url, name }, i) => (
          <li key={i}>
            <a href={url} aria-label={name} target="_blank" rel="noreferrer">
              <Icon name={name as IconName} />
            </a>
          </li>
        ))}
      <li>
        <Link to="/contact" aria-label="Contact">
          <IconEnvelope />
        </Link>
      </li>
    </StyledSocialList>
  </Side>
);

export default Social;
