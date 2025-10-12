const path = require('path');
const _ = require('lodash');
const fs = require("fs")

exports.createPages = async ({ actions, graphql, reporter }) => {
  const { createPage } = actions;
  const { createRedirect } = actions;
  const postTemplate = path.resolve(`src/frontend/templates/post.js`);
  const tagTemplate = path.resolve('src/frontend/templates/tag.js');

  const result = await graphql(`
    {
      postsRemark: allMarkdownRemark(
        filter: { fileAbsolutePath: { regex: "/src/frontend/content/posts/" } }
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
      context: { slug: pathFromFM }, // must match $slug in post template query
    });
  });

  // Derive tags from the same posts so every tag page has data
  const tagsByKey = new Map();
  posts.forEach(({ node }) => {
    const tags = node.frontmatter?.tags || [];
    tags.forEach((t) => {
      if (typeof t !== 'string') return;
      const raw = t.trim();
      if (!raw) return;
      const key = _.kebabCase(raw);
      if (!tagsByKey.has(key)) tagsByKey.set(key, new Set());
      tagsByKey.get(key).add(raw);
    });
  });

  // Create one page per kebab-cased tag
  for (const [key, set] of tagsByKey.entries()) {
    const variants = Array.from(set);
    const display = variants[0]; // pick one for the H1
    createPage({
      path: `/blog/tags/${key}/`,
      component: tagTemplate,
      context: {
        tag: display,
      },
    });
  }

  createRedirect({
    fromPath: "/archive",
    toPath: "/blog", // or "/"
    isPermanent: true,
  });
};

// Add Webpack aliases + skip browser-only libs during SSR
exports.onCreateWebpackConfig = ({ stage, loaders, actions }) => {
  // Skip modules that reference window/document during SSR
  if (stage === 'build-html' || stage === 'develop-html') {
    actions.setWebpackConfig({
      module: {
        rules: [
          { test: /scrollreveal/, use: loaders.null() },
          { test: /animejs/, use: loaders.null() },
          { test: /miniraf/, use: loaders.null() },
        ],
      },
    });
  }

  // Make alias imports like @components/... work in all stages
  actions.setWebpackConfig({
    resolve: {
      alias: {
        '@components': path.resolve(__dirname, 'src/frontend/components'),
        '@config': path.resolve(__dirname, 'src/frontend/config.js'), // file is src/config.js
        '@fonts': path.resolve(__dirname, 'src/frontend/fonts'),
        '@hooks': path.resolve(__dirname, 'src/frontend/hooks'),
        '@images': path.resolve(__dirname, 'src/frontend/images'),
        '@pages': path.resolve(__dirname, 'src/frontend/pages'),
        '@styles': path.resolve(__dirname, 'src/frontend/styles'),
        '@utils': path.resolve(__dirname, 'src/frontend/utils'),
      },
      extensions: ['.mjs', '.js', '.jsx', '.ts', '.tsx', '.json'],
    },
  });
};
