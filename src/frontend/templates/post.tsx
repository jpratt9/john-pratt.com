import React from 'react';
import { graphql, Link, HeadFC, PageProps } from 'gatsby';
import kebabCase from 'lodash/kebabCase';
import styled from 'styled-components';
import { Layout } from '@components';
import SEO from '@components/head';
import { createGlobalStyle } from 'styled-components';
import PrismStyles from '@styles/PrismStyles';
import { BlogPostFrontmatter, MarkdownNode } from '../../types';

const PrismGlobal = createGlobalStyle`${PrismStyles}`;

interface PostTemplateData {
  markdownRemark: MarkdownNode<BlogPostFrontmatter>;
}

interface PostTemplateContext {
  slug: string;
}

const StyledPostContainer = styled.main`
  max-width: 1200px;
  width: 100%;
  padding: 200px 150px;
  overflow-x: hidden;
  overflow-y: hidden;

  @media (max-width: 1080px) {
    padding: 200px 100px;
  }
  @media (max-width: 768px) {
    padding: 150px 50px;
  }
  @media (max-width: 480px) {
    padding: 125px 25px;
  }
`;
const StyledPostHeader = styled.header`
  margin-bottom: 25px;
  .tag { margin-right: 10px; }
  .post__date {
    display: block;
    margin-top: 10px;
    color: var(--slate);
    font-size: var(--fz-sm);
    font-family: var(--font-mono);
  }
`;
const StyledPostContent = styled.div`
  margin-bottom: 100px;
  overflow-x: hidden;
  overflow-y: hidden;
  h1, h2, h3, h4, h5, h6 { margin: 2em 0 1em; }
  p { margin: 1em 0; line-height: 1.5; color: var(--light-slate); }
  a { ${({ theme }) => theme.mixins.inlineLink}; }
  code { background-color: var(--lightest-navy); color: var(--lightest-slate);
         border-radius: var(--border-radius); font-size: var(--fz-sm);
         padding: 0.2em 0.4em; }
  pre { overflow-x: auto; }
  pre code { background-color: transparent; padding: 0; }
  table { border-collapse: collapse; width: 100%; margin: 1.5em 0; font-size: 0.90rem;
          display: block; overflow-x: auto; }
  th, td { border: 1px solid var(--slate); padding: 12px 15px; text-align: left;
           vertical-align: top; color: var(--lightest-slate); }
  th { font-weight: bold; }
  img { max-width: 100%; max-height: 100%; height: auto; }
`;

const PostTemplate: React.FC<PageProps<PostTemplateData, PostTemplateContext>> = ({ data, location }) => {
  const post = data?.markdownRemark;
  if (!post) return null;

  const { frontmatter, html } = post;
  const { title, date, tags, draft } = frontmatter;

  const formatDate = (dateString: string) => {
    const d = new Date(dateString);
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  };

  return (
    <Layout location={location}>
      <PrismGlobal />
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
          {date && <span className="post__date">{formatDate(date)}</span>}
        </StyledPostHeader>

        <StyledPostContent dangerouslySetInnerHTML={{ __html: html }} />
      </StyledPostContainer>
    </Layout>
  );
};

export default PostTemplate;

export const Head: HeadFC<PostTemplateData> = ({ data, location }) => {
  const fm = data?.markdownRemark?.frontmatter ?? {} as BlogPostFrontmatter;
  return (
    <SEO
      title={fm.title}
      pathname={location?.pathname}
    />
  );
};

export const pageQuery = graphql`
  query($slug: String!) {
    markdownRemark(frontmatter: { slug: { eq: $slug } }) {
      html
      frontmatter {
        title
        draft
        date
        slug
        tags
      }
    }
  }
`;
