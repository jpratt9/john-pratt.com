import React from 'react';
import { Link, graphql } from 'gatsby';
import kebabCase from 'lodash/kebabCase';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { Layout } from '@components';
import SEO from '@components/head';

const StyledTagsContainer = styled.main`
  max-width: 1000px;

  h1 { margin-bottom: 50px; }
  ul {
    color: var(--light-slate);
    li {
      font-size: var(--fz-xxl);
      a {
        color: var(--light-slate);
        .count {
          color: var(--slate);
          font-family: var(--font-mono);
          font-size: var(--fz-md);
        }
      }
    }
  }
`;

const TagsPage = ({ data, location }) => {
  const group = data?.allMarkdownRemark?.group ?? [];

  return (
    <Layout location={location}>
      <StyledTagsContainer>
        <span className="breadcrumb">
          <span className="arrow">&larr;</span>
          <Link to="/blog">All blog posts</Link>
        </span>

        <h1>Tags</h1>
        <ul className="fancy-list">
          {group.map(tag => (
            <li key={tag.fieldValue}>
              <Link to={`/blog/tags/${kebabCase(tag.fieldValue)}/`} className="inline-link">
                {tag.fieldValue} <span className="count">({tag.totalCount})</span>
              </Link>
            </li>
          ))}
        </ul>
      </StyledTagsContainer>
    </Layout> 
  );
};

TagsPage.propTypes = {
  data: PropTypes.shape({
    allMarkdownRemark: PropTypes.shape({
      group: PropTypes.arrayOf(
        PropTypes.shape({
          fieldValue: PropTypes.string.isRequired,
          totalCount: PropTypes.number.isRequired,
        }).isRequired,
      ),
    }),
  }),
  location: PropTypes.object,
};

export default TagsPage;

export function Head({ location }) {
  return <SEO title="Tags" pathname={location?.pathname} />;
}

export const pageQuery = graphql`
  query {
    allMarkdownRemark(
      limit: 2000
      filter: {
        fileAbsolutePath: { regex: "/src/frontend/content/posts/" }
        frontmatter: { draft: { ne: true } }
      }
    ) {
      group(field: { frontmatter: { tags: SELECT } }) {
        fieldValue
        totalCount
      }
    }
  }
`;
