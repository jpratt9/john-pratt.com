import { Location } from '../types';

export const mockLocation: Location = {
  pathname: '/',
  search: '',
  hash: '',
  href: 'http://localhost:8000/',
  origin: 'http://localhost:8000',
  protocol: 'http:',
  host: 'localhost:8000',
  hostname: 'localhost',
  port: '8000',
  state: {},
  key: 'initial',
};

export const mockBlogLocation: Location = {
  ...mockLocation,
  pathname: '/blog/',
  href: 'http://localhost:8000/blog/',
};

export const mockMarkdownNode = {
  id: 'test-id',
  frontmatter: {
    date: '2025-01-14',
    title: 'Test Post',
    description: 'Test description',
    slug: '/blog/test-post',
    tags: ['test', 'typescript'],
    draft: false,
    external: null,
    github: null,
    company: null,
  },
  html: '<p>Test content</p>',
  excerpt: 'Test excerpt',
};

export const mockJobNode = {
  id: 'test-job-id',
  frontmatter: {
    title: 'Software Engineer',
    company: 'Test Company',
    location: 'Remote',
    range: 'January 2020 - Present',
    url: 'https://testcompany.com',
  },
  html: '<p>Job description</p>',
};

export const mockFeaturedProject = {
  id: 'test-featured-id',
  frontmatter: {
    title: 'Featured Project',
    cover: './cover.png',
    external: 'https://example.com',
    github: 'https://github.com/test/repo',
    tech: ['React', 'TypeScript', 'Gatsby'],
    showInProjects: true,
  },
  html: '<p>Project description</p>',
};
