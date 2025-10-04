// gatsby-node.js
/*
 * Implement Gatsby's Node APIs in this file.
 *
 * See: https://www.gatsbyjs.org/docs/node-apis/
 */

const path = require('path');
const _ = require('lodash');

exports.createPages = async ({ actions, graphql, reporter }) => {
  const { createPage } = actions;
  const postTemplate = path.resolve(`src/templates/post.js`);
  const tagTemplate = path.resolve('src/templates/tag.js');

  const result = await graphql(`
    {
      postsRemark: allMarkdownRemark(
        filter: { fileAbsolutePath: { regex: "/content/posts/" } }
        sort: { frontmatter: { date: DESC } }
        limit: 1000
      ) {
        edges {
          node {
            frontmatter {
              slug
              tags
            }
          }
        }
      }
    }
  `);

  if (result.errors) {
    reporter.panicOnBuild(`Error while running GraphQL query.`);
    return;
  }

  const posts = result.data.postsRemark?.edges || [];

  // Create individual post pages
  posts.forEach(({ node }) => {
    const pathFromFM = node.frontmatter?.slug;
    if (!pathFromFM) return;

    createPage({
      path: pathFromFM,
      component: postTemplate,
      context: { slug: pathFromFM }, // match $slug in your post template query
    });
  });

  // Derive tags from the posts we just queried to avoid mismatches
  const tagSet = new Set();
  posts.forEach(({ node }) => {
    const tags = node.frontmatter?.tags;
    if (Array.isArray(tags)) {
      tags.forEach((t) => {
        if (typeof t === 'string' && t.trim()) {
          tagSet.add(t.trim()); // preserve original case for exact GraphQL match
        }
      });
    }
  });

  // Create tag pages only for tags that actually exist on posts
  Array.from(tagSet).forEach((rawTag) => {
    createPage({
      path: `/blog/tags/${_.kebabCase(rawTag)}/`,
      component: tagTemplate,
      context: { tag: rawTag }, // must match $tag in src/templates/tag.js
    });
  });
};

// https://www.gatsbyjs.org/docs/oncreatewebpackconfig/
// Fix third-party modules for SSR + provide aliases
exports.onCreateWebpackConfig = ({ stage, loaders, actions }) => {
  // Avoid SSR issues for browser-only libs
  if (stage === 'build-html' || stage === 'develop-html') {
    actions.setWebpackConfig({
      module: {
        rules: [
          {
            test: /scrollreveal/,
            use: loaders.null(),
          },
          {
            test: /animejs/,
            use: loaders.null(),
          },
          {
            test: /miniraf/,
            use: loaders.null(),
          },
        ],
      },
    });
  }

  actions.setWebpackConfig({
    resolve: {
      alias: {
        '@components': path.resolve(__dirname, 'src/components'),
        '@config': path.resolve(__dirname, 'src/config'),
        '@fonts': path.resolve(__dirname, 'src/fonts'),
        '@hooks': path.resolve(__dirname, 'src/hooks'),
        '@images': path.resolve(__dirname, 'src/images'),
        '@pages': path.resolve(__dirname, 'src/pages'),
        '@styles': path.resolve(__dirname, 'src/styles'),
        '@utils': path.resolve(__dirname, 'src/utils'),
      },
    },
  });
};