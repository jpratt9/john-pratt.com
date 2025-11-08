export const breakpoints = {
  mobile: '480px',
  tablet: '600px',
  desktop: '768px',
  wide: '1080px',
} as const;

export const media = {
  mobile: `@media (max-width: ${breakpoints.mobile})`,
  tablet: `@media (max-width: ${breakpoints.tablet})`,
  desktop: `@media (max-width: ${breakpoints.desktop})`,
  wide: `@media (max-width: ${breakpoints.wide})`,
} as const;
