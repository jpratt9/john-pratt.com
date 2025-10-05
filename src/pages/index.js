import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { Layout, Hero } from '@components';
import loadable from '@loadable/component';

const About    = loadable(() => import('@components/sections/about'    /* webpackChunkName: "about"    , webpackPrefetch: true */));
const Jobs     = loadable(() => import('@components/sections/jobs'     /* webpackChunkName: "jobs"     , webpackPrefetch: true */));
const Featured = loadable(() => import('@components/sections/featured' /* webpackChunkName: "featured" , webpackPrefetch: true */));
const Certs    = loadable(() => import('@components/sections/certs'    /* webpackChunkName: "certs"    , webpackPrefetch: true */));
const Projects = loadable(() => import('@components/sections/projects' /* webpackChunkName: "projects" , webpackPrefetch: true */));
const Contact  = loadable(() => import('@components/sections/contact'  /* webpackChunkName: "contact"  , webpackPrefetch: true */));

const StyledMainContainer = styled.main`
  counter-reset: section;
`;

const IndexPage = ({ location }) => (
  <Layout location={location}>
    <StyledMainContainer className="fillHeight">
      <Hero />
      <About />
      <Jobs />
      <Featured />
      <Certs />
      <Projects />
      <Contact />
    </StyledMainContainer>
  </Layout>
);

IndexPage.propTypes = {
  location: PropTypes.object.isRequired,
};

export default IndexPage;
