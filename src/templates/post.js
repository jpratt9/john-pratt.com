import React from 'react';
import { graphql, Link } from 'gatsby';
import kebabCase from 'lodash/kebabCase';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { Layout } from '@components';
import SEO from '@components/head'; // ⬅️ add this

const StyledPostContainer = styled.main`
  max-width: 1200px;
`;
const StyledPostHeader = styled.header`
  margin-bottom: 50px;
  .tag { margin-right: 10px; }
`;
const StyledPostContent = styled.div`
  margin-bottom: 100px;
  h1, h2, h3, h4, h5, h6 { margin: 2em 0 1em; }
  p { margin: 1em 0; line-height: 1.5; color: var(--light-slate); }
  a { ${({ theme }) => theme.mixins.inlineLink}; }
  code { background-color: var(--lightest-navy); color: var(--lightest-slate);
         border-radius: var(--border-radius); font-size: var(--fz-sm);
         padding: 0.2em 0.4em; }
  pre code { background-color: transparent; padding: 0; }
  table { border-collapse: collapse; width: 100%; margin: 1.5em 0; font-size: 0.90rem; }
  th, td { border: 1px solid var(--slate); padding: 12px 15px; text-align: left;
           vertical-align: top; color: var(--lightest-slate); }
  th { font-weight: bold; }
`;

const PostTemplate = ({ data, location }) => {
  const post = data?.markdownRemark;
  if (!post) return null;

  const { frontmatter, html } = post;
  const { title, tags, draft } = frontmatter;

  return (
    <Layout location={location}>

      <StyledPostContainer>
        <span className="breadcrumb">
          <span className="arrow">&larr;</span>
          <Link to="/blog">Blog</Link>
        </span>

        <StyledPostHeader>
          <h1 className="medium-heading">{title}</h1>
          <p className="subtitle">
            {!draft && Array.isArray(tags) && tags.length > 0 &&
              tags.map((tag, i) => (
                <Link key={i} to={`/blog/tags/${kebabCase(tag)}/`} className="tag">
                  #{tag}
                </Link>
              ))}
          </p>
        </StyledPostHeader>

        <StyledPostContent dangerouslySetInnerHTML={{ __html: html }} />
      </StyledPostContainer>
    </Layout>
  );
};

export default PostTemplate;

PostTemplate.propTypes = {
  data: PropTypes.object,
  location: PropTypes.object,
};

export function Head({ data, location }) {
  const fm = data?.markdownRemark?.frontmatter ?? {};
  return (
    <SEO
      title={fm.title}
      description={fm.description}
      pathname={location?.pathname}
    />
  );
}

export const pageQuery = graphql`
  query($slug: String!) {
    markdownRemark(frontmatter: { slug: { eq: $slug } }) {
      html
      frontmatter {
        title
        draft
        description
        date
        slug
        tags
      }
    }
  }
`;
