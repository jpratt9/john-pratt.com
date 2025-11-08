import React, { useRef } from 'react';
import { useStaticQuery, graphql } from 'gatsby';
import styled from 'styled-components';
import { media } from '@styles';
import { useScrollReveal } from '@hooks';
import { TabNavigation } from '@components';
import { CertFrontmatter, MarkdownNode, GraphQLEdge } from '../../../types';

interface CertsQueryData {
  certs: {
    edges: GraphQLEdge<CertFrontmatter>[];
  };
}

interface CertsGridProps {
  manyItems: boolean;
}

const StyledCertsSection = styled.section`
  max-width: 1000px;

  h3 {
    margin-bottom: 5px;
    font-size: var(--fz-lg);
    font-weight: 500;
    line-height: 1.3;

    a {
      ${({ theme }) => theme.mixins.inlineLink};
    }
  }

  .status {
    margin-left: 10px;
    padding: 2px 8px;
    font-size: var(--fz-xxs);
    border-radius: var(--border-radius);
    font-family: var(--font-mono);

    &.active {
      background-color: var(--green-tint);
      color: var(--green);
    }

    &.expired {
      background-color: var(--red-tint);
      color: var(--red);
    }
  }

  .dates {
    margin-bottom: 10px;
    color: var(--light-slate);
    font-family: var(--font-mono);
    font-size: var(--fz-xs);
  }
`;

const CertsGrid = styled.div<CertsGridProps>`
  display: grid;
  grid-template-columns: ${props => (props.manyItems ? 'repeat(2, 1fr)' : '1fr')};
  gap: 25px;
  width: 100%;

  ${media.desktop} {
    grid-template-columns: 1fr;
  }
`;

const CertItem = styled.div`
  width: 100%;
  background-color: var(--light-navy);
  border-radius: var(--border-radius);
  padding: 20px;
  transition: transform 0.2s ease;

  &:hover {
    transform: translateY(-5px);
  }
`;

const CertTitle = styled.div`
  display: flex;
  align-items: center;
  overflow: hidden;

  a {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
`;

const Certs: React.FC = () => {
  const data = useStaticQuery<CertsQueryData>(graphql`
    query {
      certs: allMarkdownRemark(
        filter: { fileAbsolutePath: { regex: "/src/frontend/content/certs/" } }
        sort: [{ frontmatter: { companyRank: ASC } }, { frontmatter: { certRank: ASC } }]
      ) {
        edges {
          node {
            frontmatter {
              title
              certRank
              company
              issueDate
              expiryDate
              url
              show
            }
            html
          }
        }
      }
    }
  `);

  const revealContainer = useRef<HTMLElement>(null);
  useScrollReveal(revealContainer);

  // Group certifications by company
  const groupedCerts = data.certs.edges.reduce((acc: Record<string, MarkdownNode<CertFrontmatter>[]>, { node }) => {
    const { company, show } = node.frontmatter;
    if (show !== false) {
      if (!acc[company]) {
        acc[company] = [];
      }
      acc[company].push(node);
    }
    return acc;
  }, {});

  const isCertActive = (expiryDate?: string) => {
    if (!expiryDate) return true;
    const now = new Date();
    const expiry = new Date(expiryDate);
    return now < expiry;
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long' });
  };

  const hasManyItems = (company: string): boolean => {
    return !!(groupedCerts[company] && groupedCerts[company].length > 9);
  };

  const tabs = Object.keys(groupedCerts).map(company => ({
    label: company,
    content: (
      <CertsGrid manyItems={hasManyItems(company)}>
        {groupedCerts[company]?.map((cert, j) => {
          const { frontmatter, html } = cert;
          const { title, url, issueDate, expiryDate } = frontmatter;
          const isActive = isCertActive(expiryDate);
          return (
            <CertItem key={j}>
              <h3>
                <CertTitle>
                  <a href={url} className="inline-link">
                    <span>{title}</span>
                  </a>
                  <span className={`status ${isActive ? 'active' : 'expired'}`}>
                    {isActive ? 'Active' : 'Expired'}
                  </span>
                </CertTitle>
              </h3>
              <p className="dates">
                {formatDate(issueDate)}
                {expiryDate ? ` - ${formatDate(expiryDate)}` : ' (No Expiration)'}
              </p>
              <div dangerouslySetInnerHTML={{ __html: html }} />
            </CertItem>
          );
        })}
      </CertsGrid>
    ),
  }));

  return (
    <StyledCertsSection id="certs" ref={revealContainer}>
      <h2 className="numbered-heading">My Professional Certifications</h2>
      <TabNavigation tabs={tabs} ariaLabel="Certification tabs" />
    </StyledCertsSection>
  );
};

export default Certs;
