import React, { lazy, Suspense } from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { Layout, Hero } from '@components';

const About = lazy(() => import('@components/sections/about' /* webpackChunkName: "about", webpackPrefetch: true */));
const Jobs = lazy(() => import('@components/sections/jobs' /* webpackChunkName: "jobs", webpackPrefetch: true */));
const Featured = lazy(() => import('@components/sections/featured' /* webpackChunkName: "featured", webpackPrefetch: true */));
const Certs = lazy(() => import('@components/sections/certs' /* webpackChunkName: "certs", webpackPrefetch: true */));
const Projects = lazy(() => import('@components/sections/projects' /* webpackChunkName: "projects", webpackPrefetch: true */));
const Contact = lazy(() => import('@components/sections/contact' /* webpackChunkName: "contact", webpackPrefetch: true */));

const StyledMainContainer = styled.main`
  counter-reset: section;
`;

const IndexPage = ({ location }) => (
  <Layout location={location}>
    <StyledMainContainer className="fillHeight">
      <Hero />
      <Suspense fallback={null}>
        <About />
        <Jobs />
        <Featured />
        <Certs />
        <Projects />
        <Contact />
      </Suspense>
    </StyledMainContainer>
  </Layout>
);

IndexPage.propTypes = {
  location: PropTypes.object.isRequired,
};

export default IndexPage;
 