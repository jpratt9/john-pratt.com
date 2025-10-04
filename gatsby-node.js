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
      context: { slug: pathFromFM },
    });
  });

  // Build a map: kebab-case tag -> Set of original-casing variants
  const tagsByKey = new Map();
  posts.forEach(({ node }) => {
    const tags = node.frontmatter?.tags || [];
    tags.forEach((t) => {
      if (typeof t !== 'string') return;
      const raw = t.trim();
      if (!raw) return;
      const key = _.kebabCase(raw);      // one URL per kebab-cased tag
      if (!tagsByKey.has(key)) tagsByKey.set(key, new Set());
      tagsByKey.get(key).add(raw);       // store original variants
    });
  });

  // Create one page per kebab tag, pass all original variants for filtering
  for (const [key, set] of tagsByKey.entries()) {
    const variants = Array.from(set);
    const display = variants[0]; // choose one for the H1
    createPage({
      path: `/blog/tags/${key}/`,
      component: tagTemplate,
      context: {
        tag: display,
        tagVariants: variants,    // <-- used by `in: $tagVariants` in the template
      },
    });
  }
};
