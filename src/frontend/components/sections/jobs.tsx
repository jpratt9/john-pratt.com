import React, { useRef } from 'react';
import { useStaticQuery, graphql } from 'gatsby';
import styled from 'styled-components';
import { useScrollReveal } from '@hooks';
import { TabNavigation } from '@components';
import { JobFrontmatter, GraphQLEdge } from '../../../types';

interface JobsQueryData {
  jobs: {
    edges: GraphQLEdge<JobFrontmatter>[];
  };
}

const StyledJobsSection = styled.section`
  max-width: 1000px;

  ul {
    ${({ theme }) => theme.mixins.fancyList};
  }

  h3 {
    margin-bottom: 2px;
    font-size: var(--fz-xxl);
    font-weight: 500;
    line-height: 1.3;

    .company {
      color: var(--green);
    }
  }

  .range {
    margin-bottom: 25px;
    color: var(--light-slate);
    font-family: var(--font-mono);
    font-size: var(--fz-xs);
  }
`;

const Jobs: React.FC = () => {
  const data = useStaticQuery<JobsQueryData>(graphql`
    query {
      jobs: allMarkdownRemark(
        filter: { fileAbsolutePath: { regex: "/src/frontend/content/jobs/" } }
        sort: { frontmatter: { companyRank: ASC } }
      ) {
        edges {
          node {
            frontmatter {
              title
              company
              location
              range
              url
            }
            html
          }
        }
      }
    }
  `);

  const revealContainer = useRef<HTMLElement>(null);
  useScrollReveal(revealContainer);

  const tabs = data.jobs.edges.map(({ node }) => {
    const { frontmatter, html } = node;
    const { title, url, company, range } = frontmatter;

    return {
      label: company,
      content: (
        <>
          <h3>
            <span>{title}</span>
            <span className="company">
              &nbsp;@&nbsp;
              <a href={url} className="inline-link">
                {company}
              </a>
            </span>
          </h3>

          <p className="range">{range}</p>

          <div dangerouslySetInnerHTML={{ __html: html }} />
        </>
      ),
    };
  });

  return (
    <StyledJobsSection id="jobs" ref={revealContainer}>
      <h2 className="numbered-heading">Where I've Worked</h2>
      <TabNavigation tabs={tabs} ariaLabel="Job tabs" />
    </StyledJobsSection>
  );
};

export default Jobs;
