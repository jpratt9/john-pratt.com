import React from 'react';
import { graphql, Link, HeadFC, PageProps } from 'gatsby';
import styled from 'styled-components';
import { media } from '@styles';
import { Layout } from '@components';
import { IconBookmark } from '@components/icons';
import SEO from '@components/head';
import { BlogPostFrontmatter, GraphQLEdge } from '../../../types';

interface BlogPageData {
  allMarkdownRemark: {
    edges: GraphQLEdge<BlogPostFrontmatter>[];
  };
}

const StyledMainContainer = styled.main`
  & > header {
    margin-bottom: 100px;
    text-align: center;
  }

  footer {
    ${({ theme }) => theme.mixins.flexBetween};
    width: 100%;
    margin-top: 20px;
  }
`;
const StyledGrid = styled.ul`
  ${({ theme }) => theme.mixins.resetList};
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  grid-gap: 15px;
  margin-top: 50px;
  position: relative;

  ${media.wide} {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
`;
const StyledPost = styled.li`
  transition: var(--transition);
  cursor: default;

  @media (prefers-reduced-motion: no-preference) {
    &:hover,
    &:focus-within {
      .post__inner {
        transform: translateY(-7px);
      }
    }
  }

  a {
    position: relative;
    z-index: 1;
  }

  .post__inner {
    ${({ theme }) => theme.mixins.boxShadow};
    ${({ theme }) => theme.mixins.flexBetween};
    flex-direction: column;
    align-items: flex-start;
    position: relative;
    height: 100%;
    padding: 2rem 1.75rem;
    border-radius: var(--border-radius);
    transition: var(--transition);
    background-color: var(--light-navy);

    header,
    a {
      width: 100%;
    }
  }

  .post__icon {
    ${({ theme }) => theme.mixins.flexBetween};
    color: var(--green);
    margin-bottom: 30px;
    margin-left: -5px;

    svg {
      width: 40px;
      height: 40px;
    }
  }

  .post__title {
    margin: 0 0 10px;
    color: var(--lightest-slate);
    font-size: var(--fz-xxl);

    a {
      position: static;

      &:before {
        content: '';
        display: block;
        position: absolute;
        z-index: 0;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
      }
    }
  }

  .post__desc {
    color: var(--light-slate);
    font-size: 17px;
  }

  .post__date {
    color: var(--light-slate);
    font-family: var(--font-mono);
    font-size: var(--fz-xxs);
    text-transform: uppercase;
  }

  ul.post__tags {
    display: flex;
    align-items: flex-end;
    flex-wrap: wrap;
    padding: 0;
    margin: 0;
    list-style: none;

    li {
      color: var(--green);
      font-family: var(--font-mono);
      font-size: var(--fz-xxs);
      line-height: 1.75;

      &:not(:last-of-type) {
        margin-right: 15px;
      }
    }
  }
`;

const BlogPage: React.FC<PageProps<BlogPageData>> = ({ location, data }) => {
  const posts = data.allMarkdownRemark.edges;

  return (
    <Layout location={location}>
      <StyledMainContainer>
        <header>
          <h1 className="big-heading">Blog</h1>
          <p className="subtitle">
            <span>Notes from the Field: Building, Thinking, Iterating</span>
          </p>
        </header>

        <StyledGrid>
          {posts.length > 0 &&
            posts.map(({ node }, i) => {
              const { frontmatter } = node;
              const { title, slug } = frontmatter;

              return (
                <StyledPost key={i}>
                  <div className="post__inner">
                    <header>
                      <div className="post__icon">
                        <IconBookmark />
                      </div>
                      <h5 className="post__title">
                        <Link to={slug}>{title}</Link>
                      </h5>
                    </header>
                  </div>
                </StyledPost>
              );
            })}
        </StyledGrid>
      </StyledMainContainer>
    </Layout>
  );
};

export default BlogPage;

export const Head: HeadFC = ({ location }) => {
  return (
    <SEO
      title="Blog"
      description="Notes from the Field: Building, Thinking, Iterating"
      pathname={location?.pathname}
    />
  );
};

export const pageQuery = graphql`
  {
    allMarkdownRemark(
      filter: { fileAbsolutePath: { regex: "/src/frontend/content/posts/" }, frontmatter: { draft: { ne: true } } }
      sort: {frontmatter: {date: DESC}}
    ) {
      edges {
        node {
          frontmatter {
            title
            slug
            date
            tags
            draft
          }
          html
        }
      }
    }
  }
`;
