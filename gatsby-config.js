const config = require('./src/frontend/config');
const isAnalyze = process.env.ANALYZE_BUNDLE === 'true';

const EXCLUDED_SITEMAP_PATHS = new Set([
  '/dev-404-page/',
  '/404/',
  '/404.html',
  '/offline-plugin-app-shell-fallback/',
]);

const BLOG_TAG_PREFIX = '/blog/tags/';

const toSitemapPath = (value) => {
  if (!value) return null;
  let normalized = value.trim();
  if (!normalized) return null;
  if (!normalized.startsWith('/')) {
    normalized = `/${normalized}`;
  }
  if (!normalized.endsWith('/')) {
    normalized = `${normalized}/`;
  }
  return normalized;
};
 
module.exports = {
  siteMetadata: {
    title: 'John Pratt',
    description:
      'John Pratt is a software engineer who specializes in building (and occasionally designing) top-tier digital solutions.',
    siteUrl: 'https://www.john-pratt.com', // No trailing slash allowed!
    image: '/og.png', // Path to your image you placed in the 'static' folder
  },
  trailingSlash: 'never',
  plugins: [
    `gatsby-plugin-typescript`,
    `gatsby-plugin-preact`,
    `gatsby-plugin-remove-serviceworker`,
    {
      resolve: `gatsby-plugin-sitemap`,
      options: {
        query: `
          {
            site {
              siteMetadata {
                siteUrl
              }
            }
            allSitePage {
              nodes {
                path
              }
            }
            allMarkdownRemark(
              filter: { fileAbsolutePath: { regex: "/src/frontend/content/posts/" } }
            ) {
              nodes {
                frontmatter {
                  slug
                  date
                }
              }
            }
          }
        `,
        resolveSiteUrl: ({ site }) => site.siteMetadata.siteUrl,
        resolvePages: ({ allSitePage, allMarkdownRemark }) => {
          const postsByPath = new Map();
          let latestPostTimestamp = 0;

          allMarkdownRemark.nodes.forEach((node) => {
            const slugPath = toSitemapPath(node.frontmatter?.slug);
            if (!slugPath) return;

            let lastmod;
            if (node.frontmatter?.date) {
              const timestamp = Date.parse(node.frontmatter.date);
              if (!Number.isNaN(timestamp)) {
                lastmod = new Date(timestamp).toISOString();
                if (timestamp > latestPostTimestamp) {
                  latestPostTimestamp = timestamp;
                }
              }
            }

            postsByPath.set(slugPath, { lastmod });
          });

          const latestPostIso = latestPostTimestamp ? new Date(latestPostTimestamp).toISOString() : null;

          const pages = allSitePage.nodes
            .filter(({ path }) => !EXCLUDED_SITEMAP_PATHS.has(path))
            .map(({ path }) => {
              const entry = {
                path,
                postMeta: postsByPath.get(path),
              };

              if (path === '/') {
                entry.type = 'homepage';
              } else if (path === '/blog/') {
                entry.type = 'blogIndex';
                entry.collectionLastmod = latestPostIso;
              } else if (path.startsWith(BLOG_TAG_PREFIX)) {
                entry.type = 'blogTag';
                entry.collectionLastmod = latestPostIso;
              } else if (entry.postMeta) {
                entry.type = 'blogPost';
              }

              return entry;
            });

          pages.push({
            path: '/resume.pdf',
            type: 'resume',
          });

          return pages;
        },
        serialize: (page) => {
          let changefreq = 'monthly';
          let priority = 0.5;
          let lastmod = page.postMeta?.lastmod;

          switch (page.type) {
            case 'homepage':
              changefreq = 'weekly';
              priority = 1.0;
              break;
            case 'resume':
              changefreq = 'weekly';
              priority = 1.0;
              break;
            case 'blogIndex':
              changefreq = 'daily';
              priority = 0.8;
              if (page.collectionLastmod) lastmod = page.collectionLastmod;
              break;
            case 'blogTag':
              changefreq = 'daily';
              priority = 0.6;
              if (page.collectionLastmod) lastmod = page.collectionLastmod;
              break;
            case 'blogPost':
              changefreq = 'monthly';
              priority = 0.6;
              break;
            default:
              if (page.path.startsWith('/blog/')) {
                changefreq = 'weekly';
                priority = 0.6;
              }
          }

          const entry = {
            url: page.path,
            changefreq,
            priority,
          };

          if (lastmod) {
            entry.lastmod = lastmod;
          }

          return entry;
        },
      },
    },
    {
      resolve: `gatsby-plugin-page-creator`,
      options: {
        path: `${__dirname}/src/frontend/pages`,
        ignore: ["archive.(js|ts)?(x)"]
      },
    },
    {
      resolve: `gatsby-plugin-styled-components`,
      options: {
        displayName: false,
        minify: true,
        pure: true,
        transpileTemplateLiterals: true,
        disableVendorPrefixes: true
      }
    },
    `gatsby-plugin-image`,
    `gatsby-plugin-sharp`,
    `gatsby-transformer-sharp`,
    `gatsby-plugin-robots-txt`,
    ...(isAnalyze
      ? [{
          resolve: 'gatsby-plugin-webpack-bundle-analyser-v2',
          options: { analyzerMode: 'static', openAnalyzer: false, reportFilename: 'report.html' }
        }]
    : []),
    {
      resolve: `gatsby-plugin-manifest`,
      options: {
        name: 'John Pratt',
        short_name: 'John Pratt',
        start_url: '/',
        background_color: config.colors.darkNavy,
        theme_color: config.colors.navy,
        display: 'minimal-ui',
        icon: 'src/frontend/images/logo.png',
      },
    },
    {
      resolve: `gatsby-source-filesystem`,
      options: {
        name: `images`,
        path: `${__dirname}/src/frontend/images`,
      },
    },
    {
      resolve: 'gatsby-source-filesystem',
      options: {
        name: 'content',
        path: `${__dirname}/src/frontend/content/`,
      },
    },
    {
      resolve: `gatsby-transformer-remark`,
      options: {
        plugins: [
          {
            // https://www.gatsbyjs.org/packages/gatsby-remark-external-links
            resolve: 'gatsby-remark-external-links',
            options: {
              target: '_blank',
              rel: 'nofollow noopener noreferrer',
            },
          },
          {
            // https://www.gatsbyjs.org/packages/gatsby-remark-images
            resolve: 'gatsby-remark-images',
            options: {
              maxWidth: 700,
              linkImagesToOriginal: true,
              quality: 90,
              backgroundColor: config.colors.green,
            },
          },
          {
            // https://www.gatsbyjs.org/packages/gatsby-remark-code-titles/
            resolve: 'gatsby-remark-code-titles',
          }, // IMPORTANT: this must be ahead of other plugins that use code blocks
          {
            // https://www.gatsbyjs.org/packages/gatsby-remark-prismjs
            resolve: `gatsby-remark-prismjs`,
            options: {
              classPrefix: 'language-',
              inlineCodeMarker: null,
              aliases: {},
              showLineNumbers: false,
              noInlineHighlight: false,

              languageExtensions: [
                {
                  language: 'superscript',
                  extend: 'javascript',
                  definition: {
                    superscript_types: /(SuperType)/,
                  },
                  insertBefore: {
                    function: {
                      superscript_keywords: /(superif|superelse)/,
                    },
                  },
                },
              ],
              // Customize the prompt used in shell output
              // Values below are default
              prompt: {
                user: 'root',
                host: 'localhost',
                global: false,
              },
            },
          },
        ],
      },
    },
    {
      resolve: `gatsby-plugin-google-gtag`,
      options: {
        trackingIds: ['G-ZFHREMYV1Q'],
        gtagConfig: {
          anonymize_ip: true,
          send_page_view: false,   // set true/omit if you want the default auto pageview
        },

        // Plugin-level config
        pluginConfig: {
          head: true,
          respectDNT: true,
          exclude: ["/preview/**"],
          delayOnRouteUpdate: 0,
        },
      },
      
    },
  ],
};
