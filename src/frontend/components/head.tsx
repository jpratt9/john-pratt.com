import React from 'react';
import { useStaticQuery, graphql } from 'gatsby';

interface HeadProps {
  title?: string | null;
  description?: string | null;
  image?: string | null;
  pathname?: string;
  noIndex?: boolean;
}

interface SiteMetadata {
  defaultTitle: string;
  defaultDescription: string;
  siteUrl: string;
  defaultImage: string;
}

interface HeadQueryData {
  site: {
    siteMetadata: SiteMetadata;
  };
}

const Head: React.FC<HeadProps> = ({ title, description, image, pathname = '', noIndex }) => {
  const { site } = useStaticQuery<HeadQueryData>(graphql`
    query {
      site {
        siteMetadata {
          defaultTitle: title
          defaultDescription: description
          siteUrl
          defaultImage: image
        }
      }
    }
  `);

  const { defaultTitle, defaultDescription, siteUrl, defaultImage } =
    site.siteMetadata;

  const seo = {
    title: title || defaultTitle,
    description: description || defaultDescription,
    image: `${siteUrl}${image || defaultImage}`,
    url: `${siteUrl}${pathname}`,
  };

  const fullTitle = title ? `${title} | ${defaultTitle}` : defaultTitle;

  return (
    <>
      {/* Head API supports editing <html> attributes */}
      <html lang="en" />

      <title>{fullTitle}</title>

      {noIndex && <meta name="robots" content="noindex" />}
      <meta name="description" content={seo.description} />
      <meta name="image" content={seo.image} />

      <meta property="og:title" content={seo.title} />
      <meta property="og:description" content={seo.description} />
      <meta property="og:image" content={seo.image} />
      <meta property="og:url" content={seo.url} />
      <meta property="og:type" content="website" />

      <meta
        name="google-site-verification"
        content="DCl7VAf9tcz6eD9gb67NfkNnJ1PKRNcg8qQiwpbx9Lk"
      />
    </>
  );
};

export default Head;
