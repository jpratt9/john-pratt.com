import React from 'react';
import { Link } from 'gatsby';

interface NavLinkProps {
  url: string;
  name: string;
}

export const NavLink: React.FC<NavLinkProps> = ({ url, name }) => {
  return url.endsWith('.pdf') ? (
    <a href={url} target="_blank" rel="noopener noreferrer">
      {name}
    </a>
  ) : (
    <Link to={url}>{name}</Link>
  );
};

export default NavLink;
