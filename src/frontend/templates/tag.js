import React from 'react';
import { Link, graphql } from 'gatsby';
import kebabCase from 'lodash/kebabCase';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { Layout } from '@components';
import SEO from '@components/head';

const StyledTagsContainer = styled.main`
  max-width: 1000px;

  a { ${({ theme }) => theme.mixins.inlineLink}; }

  h1 {
    ${({ theme }) => theme.mixins.flexBetween};
    margin-bottom: 50px;
    a { font-size: var(--fz-lg); font-weight: 400; }
  }

  ul li { font-size: 24px; }
  ul li h2 { font-size: inherit; margin: 0; }
  ul li h2 a { color: var(--light-slate); }

  .subtitle { color: var(--slate); font-size: var(--fz-sm); }
  .subtitle .tag { margin-right: 10px; }
`;

const TagTemplate = ({ pageContext, data, location }) => {
  const displayTag = pageContext?.tag ?? '';
  const allEdges = data?.allMarkdownRemark?.edges ?? [];

  // Case-insensitive match of the tag against string tags[]
  const edges = allEdges.filter(({ node }) => {
    const tags = node.frontmatter?.tags || [];
    return tags.some(t => (t || '').toLowerCase() === displayTag.toLowerCase());
  });

  return (
    <Layout location={location}>
      <StyledTagsContainer>
        <span className="breadcrumb">
          <span className="arrow">&larr;</span>
          <Link to="/blog">All blog posts</Link>
        </span>

        <h1>
          <span>#{displayTag}</span>
          <span><Link to="/blog/tags">View all tags</Link></span>
        </h1>

        {edges.length === 0 ? (
          <p>No posts found for this tag.</p>
        ) : (
          <ul className="fancy-list">
            {edges.map(({ node }) => {
              const { title, slug, date, tags } = node.frontmatter;
              return (
                <li key={slug}>
                  <h2><Link to={slug}>{title}</Link></h2>
                  <p className="subtitle">
                    <time>
                      {new Date(date).toLocaleDateString('en-US', {
                        year: 'numeric', month: 'long', day: 'numeric',
                      })}
                    </time>
                    <span>&nbsp;&mdash;&nbsp;</span>
                    {tags?.length > 0 && tags.map((t, i) => (
                      <Link key={i} to={`/blog/tags/${kebabCase(t)}/`} className="tag">
                        #{t}
                      </Link>
                    ))}
                  </p>
                </li>
              );
            })}
          </ul>
        )}
      </StyledTagsContainer>
    </Layout>
  );
};

export default TagTemplate;

TagTemplate.propTypes = {
  pageContext: PropTypes.shape({ tag: PropTypes.string.isRequired }),
  data: PropTypes.shape({
    allMarkdownRemark: PropTypes.shape({
      edges: PropTypes.arrayOf(
        PropTypes.shape({
          node: PropTypes.shape({
            frontmatter: PropTypes.shape({
              title: PropTypes.string.isRequired,
            }),
          }),
        }).isRequired,
      ),
    }),
  }),
  location: PropTypes.object,
};

export function Head({ location, pageContext }) {
  const displayTag = pageContext?.tag;
  return <SEO title={`Tagged: #${displayTag}`} pathname={location?.pathname} />;
}

// No variables - fetch posts once, filter in JS
export const pageQuery = graphql`
  {
    allMarkdownRemark(
      limit: 2000
      sort: { frontmatter: { date: DESC } }
      filter: {
        fileAbsolutePath: { regex: "/src/frontend/content/posts/" }
        frontmatter: { draft: { ne: true } }
      }
    ) {
      edges {
        node {
          frontmatter {
            title
            date
            slug
            tags
          }
        }
      }
    }
  }
`;
