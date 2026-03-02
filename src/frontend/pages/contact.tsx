import React, { useState } from 'react';
import { HeadFC } from 'gatsby';
import styled from 'styled-components';
import { Layout } from '@components';
import SEO from '@components/head';
import { PageProps } from '../../types';

const CONTACT_API_URL = process.env.GATSBY_CONTACT_API_URL || '';

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

  .hp-field {
    position: absolute;
    left: -9999px;
    opacity: 0;
    height: 0;
    width: 0;
    overflow: hidden;
  }

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

  input:not([type='checkbox']),
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

  .opt-in {
    p {
      color: var(--slate);
      font-size: var(--fz-sm);
      line-height: 1.5;
      margin: 0 0 10px;
    }

    .checkbox {
      flex-direction: row;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      color: var(--slate);

      input[type='checkbox'] {
        appearance: none;
        width: 16px;
        height: 16px;
        min-width: 16px;
        background-color: var(--light-navy);
        border: 1px solid var(--lightest-navy);
        border-radius: 2px;
        cursor: pointer;
        position: relative;

        &:checked {
          background-color: var(--green);
          border-color: var(--green);

          &::after {
            content: '✓';
            position: absolute;
            top: -1px;
            left: 2px;
            color: var(--navy);
            font-size: 12px;
            font-weight: bold;
          }
        }
      }
    }
  }

  .error-message {
    color: #ff6464;
    font-size: var(--fz-sm);
    text-align: center;
  }

  button {
    ${({ theme }) => theme.mixins.bigButton};
    align-self: center;
    margin-top: 10px;
    cursor: pointer;
    background: none;

    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  }
`;

type FormStatus = 'idle' | 'submitting' | 'success' | 'error';

const ContactPage: React.FC<PageProps> = ({ location }) => {
  const [status, setStatus] = useState<FormStatus>('idle');
  const [errorMessage, setErrorMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setStatus('submitting');
    setErrorMessage('');

    const form = e.currentTarget;
    const formData = new FormData(form);
    const data: Record<string, string | boolean> = {};
    formData.forEach((value, key) => {
      data[key] = key === 'optIn' ? true : value.toString();
    });
    if (!data.optIn) data.optIn = false;

    try {
      const res = await fetch(CONTACT_API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.error || 'Something went wrong');
      }

      setStatus('success');
      form.reset();
    } catch (err) {
      setStatus('error');
      setErrorMessage(err instanceof Error ? err.message : 'Something went wrong');
    }
  };

  if (status === 'success') {
    return (
      <Layout location={location}>
        <StyledMainContainer>
          <StyledContactPage>
            <span className="overline">Thank You</span>
            <h1 className="title">Message Sent</h1>
            <p className="description">I'll get back to you as soon as possible.</p>
            <StyledForm as="div">
              <button type="button" onClick={() => setStatus('idle')}>
                Send Another Message
              </button>
            </StyledForm>
          </StyledContactPage>
        </StyledMainContainer>
      </Layout>
    );
  }

  return (
    <Layout location={location}>
      <StyledMainContainer>
        <StyledContactPage>
          <span className="overline">Get In Touch</span>
          <h1 className="title">Contact Me</h1>
          <p className="description">
            Have a project in mind or want to discuss an opportunity? Fill out the form below and
            I'll get back to you as soon as possible.
          </p>

          <StyledForm onSubmit={handleSubmit}>
            <div className="hp-field">
              <label>
                Website
                <input type="text" name="website" tabIndex={-1} autoComplete="off" />
              </label>
            </div>

            <div className="name-row">
              <label>
                First Name*
                <input type="text" name="firstName" placeholder="First name" required />
              </label>
              <label>
                Last Name*
                <input type="text" name="lastName" placeholder="Last name" required />
              </label>
            </div>

            <label>
              Email*
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
              Message*
              <textarea name="message" required />
            </label>

            <div className="opt-in">
              <p>
                I want to receive emails from Pratt Solutions about products, services, events,
                &amp; thought leadership.
              </p>
              <label className="checkbox">
                <input type="checkbox" name="optIn" />
                Yes
              </label>
            </div>

            {status === 'error' && (
              <p className="error-message">
                {errorMessage || 'Something went wrong. Please try again.'}
              </p>
            )}

            <button type="submit" disabled={status === 'submitting'}>
              {status === 'submitting' ? 'Sending...' : 'Submit'}
            </button>
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
};

export default ContactPage;

export const Head: HeadFC = ({ location }) => {
  return <SEO title="Contact" pathname={location?.pathname} />;
};
