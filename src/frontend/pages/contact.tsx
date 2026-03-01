import React from 'react';
import { HeadFC } from 'gatsby';
import styled from 'styled-components';
import { Layout } from '@components';
import SEO from '@components/head';
import { PageProps } from '../../types';

const StyledMainContainer = styled.main`
  ${({ theme }) => theme.mixins.flexCenter};
  flex-direction: column;
  min-height: 100vh;
  padding-top: 100px;
`;

const StyledContactPage = styled.div`
  max-width: 600px;
  width: 100%;
  text-align: center;

  .overline {
    display: block;
    margin-bottom: 20px;
    color: var(--green);
    font-family: var(--font-mono);
    font-size: var(--fz-md);
    font-weight: 400;
  }

  .title {
    font-size: clamp(40px, 5vw, 60px);
    margin-bottom: 20px;
  }

  .description {
    margin-bottom: 50px;
  }

  .skip-the-line {
    margin-top: 40px;
    text-align: center;
    color: var(--slate);
    font-size: var(--fz-xl);
    line-height: 1.5;

    hr {
      border: none;
      border-top: 1px solid var(--lightest-navy);
      margin-bottom: 20px;
    }

    a {
      color: var(--green);
      text-decoration: none;

      &:hover {
        text-decoration: underline;
      }
    }
  }
`;

const StyledForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: 20px;
  text-align: left;

  .name-row {
    display: flex;
    gap: 20px;

    label {
      flex: 1;
    }
  }

  label {
    font-family: var(--font-mono);
    font-size: var(--fz-xs);
    color: var(--green);
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  input,
  textarea {
    background-color: var(--light-navy);
    border: 1px solid var(--lightest-navy);
    border-radius: var(--border-radius);
    color: var(--lightest-slate);
    font-family: var(--font-sans);
    font-size: var(--fz-md);
    height: 50px;
    padding: 0 16px;
    line-height: 50px;
    outline: none;
    transition: var(--transition);
    width: 100%;
    box-sizing: border-box;

    &:focus {
      border-color: var(--green);
    }

    &::placeholder {
      color: var(--dark-slate);
    }
  }

  textarea {
    padding: 0 16px;
    resize: none;
    min-height: 150px;
  }

  button {
    ${({ theme }) => theme.mixins.bigButton};
    align-self: center;
    margin-top: 10px;
    cursor: pointer;
    background: none;
  }
`;

const ContactPage: React.FC<PageProps> = ({ location }) => (
  <Layout location={location}>
    <StyledMainContainer>
      <StyledContactPage>
        <span className="overline">Get In Touch</span>
        <h1 className="title">Contact Me</h1>
        <p className="description">
          Have a project in mind or want to discuss an opportunity? Fill out the form below and I'll
          get back to you as soon as possible.
        </p>

        <StyledForm>
          <div className="name-row">
            <label>
              First Name
              <input type="text" name="firstName" placeholder="First name" required />
            </label>
            <label>
              Last Name
              <input type="text" name="lastName" placeholder="Last name" required />
            </label>
          </div>

          <label>
            Email
            <input type="email" name="email" placeholder="your@email.com" required />
          </label>

          <label>
            Phone
            <input type="tel" name="phone" placeholder="(555) 555-5555" />
          </label>

          <label>
            Company
            <input type="text" name="company" placeholder="Your company" />
          </label>

          <label>
            Message
            <textarea name="message" required />
          </label>

          <button type="submit">Submit</button>
        </StyledForm>

        <div className="skip-the-line">
          <hr />
          Need to skip the line?{' '}
          <a href="https://calendly.com/johnpratt439/intro" target="_blank" rel="noreferrer">
            Book a call directly
          </a>{' '}
          and let's talk.
        </div>
      </StyledContactPage>
    </StyledMainContainer>
  </Layout>
);

export default ContactPage;

export const Head: HeadFC = ({ location }) => {
  return <SEO title="Contact" pathname={location?.pathname} />;
};
