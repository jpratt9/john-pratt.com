import { IGatsbyImageData } from 'gatsby-plugin-image';

// Location object from Gatsby
export interface Location {
  pathname: string;
  search: string;
  hash: string;
  href: string;
  origin: string;
  protocol: string;
  host: string;
  hostname: string;
  port: string;
  state?: unknown;
  key?: string;
}

// Page context from Gatsby
export interface PageContext {
  [key: string]: unknown;
}

// Page props
export interface PageProps<TData = unknown, TContext = PageContext> {
  location: Location;
  pageContext: TContext;
  data?: TData;
  children?: React.ReactNode;
}

// Config types
export interface SocialMedia {
  name: string;
  url: string;
}

export interface NavLink {
  name: string;
  url: string;
}

export interface SiteConfig {
  email: string;
  socialMedia: SocialMedia[];
  navLinks: NavLink[];
  colors: {
    green: string;
    navy: string;
    darkNavy: string;
  };
  srConfig: (delay?: number, viewFactor?: number) => ScrollRevealConfig;
}

export interface ScrollRevealConfig {
  origin: string;
  distance: string;
  duration: number;
  delay: number;
  rotate: { x: number; y: number; z: number };
  opacity: number;
  scale: number;
  easing: string;
  mobile: boolean;
  reset: boolean;
  useDelay: string;
  viewFactor: number;
  viewOffset: { top: number; right: number; bottom: number; left: number };
}

// Markdown frontmatter types
export interface JobFrontmatter {
  title: string;
  company: string;
  location: string;
  range: string;
  url: string;
  companyRank?: number;
}

export interface CertFrontmatter {
  title: string;
  certRank: number;
  company: string;
  issueDate: string;
  expiryDate?: string;
  url: string;
  show?: boolean;
  companyRank?: number;
}

export interface FeaturedProjectFrontmatter {
  title: string;
  cover: {
    childImageSharp: {
      gatsbyImageData: IGatsbyImageData;
    };
  };
  tech: string[];
  classified?: boolean;
  github?: string;
  external?: string;
  date?: string;
}

export interface BlogPostFrontmatter {
  title: string;
  slug: string;
  date: string;
  tags: string[];
  draft?: boolean;
  description?: string;
}

// GraphQL node types
export interface MarkdownNode<T> {
  frontmatter: T;
  html: string;
}

export interface GraphQLEdge<T> {
  node: MarkdownNode<T>;
}

export interface GraphQLConnection<T> {
  edges: GraphQLEdge<T>[];
}

// Hook return types
export type ScrollDirection = 'up' | 'down';

export interface UseScrollDirectionOptions {
  initialDirection?: ScrollDirection;
  thresholdPixels?: number;
  off?: boolean;
}
