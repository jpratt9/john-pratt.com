import React, { useEffect, useRef } from 'react';
import { useStaticQuery, graphql } from 'gatsby';
import { GatsbyImage, getImage, IGatsbyImageData } from 'gatsby-plugin-image';
import styled from 'styled-components';
import { media } from '@styles';
import { getSr } from '@utils/sr';
import config from '@config';
import { Icon } from '@components/icons';
import { usePrefersReducedMotion } from '@hooks';
import { FeaturedProjectFrontmatter, GraphQLEdge } from '../../../types';

const { srConfig } = config;

interface FeaturedQueryData {
  featured: {
    edges: GraphQLEdge<FeaturedProjectFrontmatter>[];
  };
}

const StyledProjectsGrid = styled.ul`
  ${({ theme }) => theme.mixins.resetList};

  a {
    position: relative;
    z-index: 1;
  }
`;

const StyledProject = styled.li`
  position: relative;
  display: grid;
  grid-gap: 10px;
  grid-template-columns: repeat(12, 1fr);
  align-items: center;

  ${media.desktop} {
    ${({ theme }) => theme.mixins.boxShadow};
  }

  &:not(:last-of-type) {
    margin-bottom: 100px;

    ${media.desktop} {
      margin-bottom: 70px;
    }

    ${media.mobile} {
      margin-bottom: 30px;
    }
  }

  &:nth-of-type(even) {
    .project-tech-list {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      padding: 0;
      margin: 10px 0 0 0;
      list-style: none;

      ${media.desktop} {
        justify-content: center;
      }

      li {
        margin: 0 0 5px 20px;

        ${media.desktop} {
          margin: 0 10px 5px 0;
        }
      }
    }
  }

  &:nth-of-type(odd) {
    .project-content {
      grid-column: 7 / -1;
      text-align: right;

      ${media.wide} {
        grid-column: 5 / -1;
      }
      ${media.desktop} {
        grid-column: 1 / -1;
        padding: 40px 40px 30px;
        text-align: left;
      }
      ${media.mobile} {
        padding: 25px 25px 20px;
      }
    }
    .project-tech-list {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      padding: 0;
      margin: 10px 0 0 0;
      list-style: none;

      ${media.desktop} {
        justify-content: center;
      }

      li {
        margin: 0 0 5px 20px;

        ${media.desktop} {
          margin: 0 10px 5px 0;
        }
      }
    }
    .project-links {
      justify-content: flex-end;
      margin-left: 0;
      margin-right: -10px;
      margin-bottom: 20px;

      ${media.desktop} {
        justify-content: flex-start;
        margin-left: -10px;
        margin-right: 0;
        margin-bottom: 20px;
      }
    }
    .project-image {
      grid-column: 1 / 8;

      ${media.desktop} {
        grid-column: 1 / -1;
      }
    }
  }

  .project-content {
    position: relative;
    grid-column: 1 / 7;
    grid-row: 1 / -1;

    ${media.wide} {
      grid-column: 1 / 9;
    }

    ${media.desktop} {
      display: flex;
      flex-direction: column;
      justify-content: center;
      height: 100%;
      grid-column: 1 / -1;
      padding: 40px 40px 30px;
      z-index: 5;
    }

    ${media.mobile} {
      padding: 30px 25px 20px;
    }
  }

  .project-overline {
    margin: 10px 0;
    color: var(--green);
    font-family: var(--font-mono);
    font-size: var(--fz-xs);
    font-weight: 400;
  }

  .project-title {
    color: var(--lightest-slate);
    font-size: clamp(24px, 5vw, 28px);

    @media (min-width: 768px) {
      margin: 0 0 20px;
    }

    ${media.desktop} {
      color: var(--white);

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
  }

  .project-description {
    ${({ theme }) => theme.mixins.boxShadow};
    position: relative;
    z-index: 2;
    padding: 25px;
    border-radius: var(--border-radius);
    background-color: var(--light-navy);
    color: var(--light-slate);
    font-size: var(--fz-lg);

    ${media.desktop} {
      padding: 20px 0;
      background-color: transparent;
      box-shadow: none;

      &:hover {
        box-shadow: none;
      }
    }

    a {
      ${({ theme }) => theme.mixins.inlineLink};
    }

    strong {
      color: var(--white);
      font-weight: normal;
    }
  }

  .project-tech-list {
    display: flex;
    flex-wrap: wrap;
    position: relative;
    z-index: 2;
    margin: 25px 0 10px;
    padding: 0;
    list-style: none;

    li {
      margin: 0 20px 5px 0;
      color: var(--light-slate);
      font-family: var(--font-mono);
      font-size: var(--fz-xs);
      white-space: nowrap;
      text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.4);
      font-weight: bold;
    }

    ${media.desktop} {
      margin: 10px 0;

      li {
        margin: 0 10px 5px 0;
        color: var(--lightest-slate);
      }
    }
  }

  .project-links {
    display: flex;
    align-items: center;
    position: relative;
    margin-top: 10px;
    margin-left: -10px;
    color: var(--lightest-slate);
    margin-bottom: 20px;

    a {
      ${({ theme }) => theme.mixins.flexCenter};
      padding: 10px;

      &.external {
        svg {
          width: 22px;
          height: 22px;
          margin-top: -4px;
        }
      }

      svg {
        width: 20px;
        height: 20px;
      }
    }
  }

  .project-image {
    grid-column: 6 / -1;
    grid-row: 1 / -1;
    position: relative;
    z-index: 1;

    ${media.desktop} {
      grid-column: 1 / -1;
      height: 100%;
      opacity: 0.25;
    }

    a {
      width: 100%;
      height: 100%;
      border-radius: var(--border-radius);
      vertical-align: middle;

      &:hover,
      &:focus {
        background: transparent;
        outline: 0;

        &:before,
        .img {
          background: transparent;
          filter: none;
        }
      }

      &:before {
        content: '';
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 3;
        transition: var(--transition);
        background-color: var(--navy);
        mix-blend-mode: screen;
      }
    }

    .img {
      border-radius: var(--border-radius);
      filter: blur(1px);
      transition: var(--transition);

      ${media.desktop} {
        object-fit: cover;
        width: auto;
        height: 100%;
        filter: grayscale(100%) contrast(1) brightness(50%);
      }
    }
  }
`;

const Featured: React.FC = () => {
  const data = useStaticQuery<FeaturedQueryData>(graphql`
    {
      featured: allMarkdownRemark(
        filter: { fileAbsolutePath: { regex: "/src/frontend/content/featured/" } }
        sort: { frontmatter: { date: ASC } }
      ) {
        edges {
          node {
            frontmatter {
              title
              cover {
                childImageSharp {
                  gatsbyImageData(width: 700, placeholder: BLURRED, formats: [AUTO, WEBP, AVIF])
                }
              }
              tech
              classified
              github
              external
            }
            html
          }
        }
      }
    }
  `);

  const featuredProjects = data.featured.edges.filter(({ node }) => node);
  const revealTitle = useRef<HTMLHeadingElement>(null);
  const revealProjects = useRef<(HTMLLIElement | null)[]>([]);
  const prefersReducedMotion = usePrefersReducedMotion();

  useEffect(() => {
    if (prefersReducedMotion) return;

    let mounted = true;

    (async () => {
      const sr = await getSr();
      if (!mounted || !sr) return;

      if (revealTitle.current) {
        sr.reveal(revealTitle.current, srConfig());
      }

      revealProjects.current.forEach((ref, i) => {
        if (ref) sr.reveal(ref, srConfig(i * 100));
      });
    })();

    return () => {
      mounted = false;
    };
  }, [prefersReducedMotion]);

  return (
    <section id="projects">
      <h2 className="numbered-heading" ref={revealTitle}>
        Some Things I've Built
      </h2>

      <StyledProjectsGrid>
        {featuredProjects &&
          featuredProjects.map(({ node }, i) => {
            const { frontmatter, html } = node;
            const { external, title, tech, github, cover, classified } = frontmatter;
            const image = getImage(cover) as IGatsbyImageData;

            return (
              <StyledProject
                key={i}
                ref={el => {
                  revealProjects.current[i] = el;
                }}
              >
                <div className="project-content">
                  <div>
                    <h3
                      className="project-title"
                      style={{ fontStyle: classified ? 'italic' : 'normal' }}
                    >
                      <a href={external}>{title}</a>
                    </h3>

                    <div className="project-description" dangerouslySetInnerHTML={{ __html: html }} />

                    {tech && tech.length > 0 && (
                      <ul className="project-tech-list">
                        {tech.map((techItem: string, j: number) => (
                          <li key={j}>{techItem}</li>
                        ))}
                      </ul>
                    )}

                    <div className="project-links">
                      {github && (
                        <a href={github} aria-label="GitHub Link">
                          <Icon name="GitHub" />
                        </a>
                      )}
                      {external && (
                        <a href={external} aria-label="External Link" className="external">
                          <Icon name="External" />
                        </a>
                      )}
                    </div>
                  </div>
                </div>

                <div className="project-image">
                  <a href={external ? external : github ? github : '#'}>
                    {image && <GatsbyImage image={image} alt={title} className="img" />}
                  </a>
                </div>
              </StyledProject>
            );
          })}
      </StyledProjectsGrid>
    </section>
  );
};

export default Featured;
