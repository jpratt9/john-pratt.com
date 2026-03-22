import React, { useRef } from 'react';
import styled, { keyframes } from 'styled-components';
import { useScrollReveal } from '@hooks';
import { media } from '@styles';
import meghAvatar from '@images/testimonials/megh.jpeg';
import neilAvatar from '@images/testimonials/neil.png';
import dustinAvatar from '@images/testimonials/dustin.jpg';
import lackeyAvatar from '@images/testimonials/lackey.jpg';
import rohanAvatar from '@images/testimonials/rohan.jpeg';
import trevorAvatar from '@images/testimonials/trevor.jpeg';
import chadAvatar from '@images/testimonials/chad.jpeg';
import emilyAvatar from '@images/testimonials/emily.jpeg';
import helalAvatar from '@images/testimonials/helal.jpeg';
import jeffreyAvatar from '@images/testimonials/jeffrey-yao.jpeg';
import jeffordAvatar from '@images/testimonials/jefford.jpg';
import mayaAvatar from '@images/testimonials/maya.jpg';
import pottsAvatar from '@images/testimonials/john-potts.jpeg';

const testimonials = [
  {
    quote:
      'John led a client cloud migration project we did through Pratt Solutions, acting as our technical lead. He was a pleasure to work with & very professional!',
    name: 'Megh Deshpande',
    role: 'Full Stack Developer, Kewordal',
    avatar: meghAvatar,
  },
  {
    quote:
      'John and I have bounced ideas off each other on everything from career networking and sales to automating full stack applications across Android, iOS, and web. He knows his stuff across the stack, and brings good technical and business insight to the table.',
    name: 'Neil Chainani',
    role: 'Software Developer, CDC',
    avatar: neilAvatar,
  },
  {
    quote:
      'John\'s work is top notch. Fast turnaround with all the features I needed. He was able to create a website that helped me reach more clients and enhance my professional credibility, allowing me to charge more for my coaching service. He was attentive to suggestions and communicates quickly and clearly. You can tell he really cares about his work and prioritizes customer satisfaction.',
    name: 'Dustin Lewis',
    role: 'English Tutor @ Preply',
    avatar: dustinAvatar,
  },
  {
    quote:
      'John has been a great teacher and coach for me. He\'s helped me improve my confidence and networking skills in so many ways, and opened my eyes to things I realize are really important now.',
    name: 'Andrew Lackey',
    role: 'Student, University of North Carolina at Charlotte',
    avatar: lackeyAvatar,
  },
  {
    quote:
      'John was my TDP mentor when I first joined Capital One under the Technology Development Program. He readily offered career advice and made sure I was able to get up to speed quickly with company culture.',
    name: 'Rohan Upponi',
    role: 'Software Engineer, Capital One',
    avatar: rohanAvatar,
  },
  {
    quote:
      'John was my TDP mentor while I was a Capital One intern. We did biweekly check-ins where he made sure everything went smoothly with my team and was a major reason I received and accepted a full-time offer.',
    name: 'Trevor White',
    role: 'Software Engineer Intern, Capital One',
    avatar: trevorAvatar,
  },
  {
    quote:
      'John was my TDP mentor during my first rotation with the company and was a major asset to a smooth transition into fulltime employment with the company.',
    name: 'Chad Mustard',
    role: 'Software Engineer, Capital One',
    avatar: chadAvatar,
  },
  {
    quote:
      'After working together at Capital One, John referred me to an opportunity at Duke Energy where I went on to work for 3 years as a Software Engineer SME.',
    name: 'Emily Broom',
    role: 'Senior Software Engineer, Oracle',
    avatar: emilyAvatar,
  },
  {
    quote:
      'John was my TDP buddy during my Capital One internship. When I ended up on a tech stack that wasn\'t the right fit, he advocated for me and helped me switch to a project more aligned with my interests.',
    name: 'Helal Chowdhury',
    role: 'Software Engineer, Bloomberg',
    avatar: helalAvatar,
  },
  {
    quote:
      'John was my TDP buddy when I joined Capital One as an Associate Engineer straight out of college during the pandemic. He helped me navigate the remote environment and connect more deeply with my team.',
    name: 'Jeffrey Yao',
    role: 'Senior Software Engineer, Capital One',
    avatar: jeffreyAvatar,
  },
  {
    quote:
      'John was our Tech Lead on a contract through Pratt Solutions where we rebuilt a client\'s Python aerospace application from the ground up. He brought in best practices like automated testing, CI/CD, and scalable data engineering patterns that elevated the entire team\'s output.',
    name: 'Jefford Mamacus',
    role: 'Head of Research and Training, Ingenuity Global Consulting',
    avatar: jeffordAvatar,
  },
  {
    quote:
      'John is a driven and organized leader. Working with him at Pratt Solutions, I saw firsthand how he manages multiple priorities while keeping his team aligned and focused on results.',
    name: 'Maya Madlangbayan',
    role: 'Principal Recruiter, Pratt Solutions',
    avatar: mayaAvatar,
  },
  {
    quote:
      'John took the lead on backend and DevOps for Orbit, acting as a key asset in digitizing our data collection across the south and midwest, and bringing invaluable insights on software best practices like unit testing and public cloud.',
    name: 'John Potts',
    role: 'Principal Engineer, Duke Energy',
    avatar: pottsAvatar,
  },
];

// Split into two rows
const row1 = testimonials;
const row2 = [...testimonials].reverse();

const scrollLeft = keyframes`
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
`;

const scrollRight = keyframes`
  0% { transform: translateX(-50%); }
  100% { transform: translateX(0); }
`;

const StyledSection = styled.section`
  padding: 100px 0;
  overflow: hidden;

  ${media.desktop} {
    padding: 80px 0;
  }
  ${media.tablet} {
    padding: 60px 0;
  }
`;

const StyledHeading = styled.h2`
  text-align: center;
  font-family: var(--font-sans);
  font-size: clamp(24px, 5vw, var(--fz-heading));
  color: var(--lightest-slate);
  margin-bottom: 50px;
`;

const StyledMarqueeRow = styled.div<{ direction: 'left' | 'right' }>`
  display: flex;
  gap: 24px;
  width: max-content;
  animation: ${({ direction }) => (direction === 'left' ? scrollLeft : scrollRight)}
    35s linear infinite;
  margin-bottom: 24px;

  &:hover {
    animation-play-state: paused;
  }

  ${media.tablet} {
    gap: 16px;
    margin-bottom: 16px;
    animation-duration: 25s;
  }
`;

const StyledCard = styled.div`
  flex-shrink: 0;
  width: 340px;
  background-color: var(--light-navy);
  border-radius: var(--border-radius);
  padding: 28px;
  font-family: var(--font-sans);
  transition: var(--transition);

  &:hover {
    transform: translateY(-5px);
  }

  ${media.desktop} {
    width: 300px;
    padding: 24px;
  }
  ${media.mobile} {
    width: 260px;
    padding: 20px;
  }
`;

const StyledQuoteMark = styled.span`
  font-family: Georgia, serif;
  font-size: 48px;
  line-height: 1;
  color: var(--green);
  display: block;
  margin-bottom: 8px;
`;

const StyledQuoteText = styled.p`
  font-size: var(--fz-md);
  color: var(--light-slate);
  line-height: 1.6;
  margin-bottom: 20px;
`;

const StyledAuthor = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const StyledAvatarWrapper = styled.div`
  width: 40px;
  height: 40px;
  min-width: 40px;
  border-radius: 50%;
  overflow: hidden;
  background-color: var(--light-navy);
  display: flex;
  align-items: center;
  justify-content: center;
`;

const StyledAvatar = styled.img`
  height: 100%;
  width: auto;
  object-fit: contain;
`;

const StyledAuthorInfo = styled.div`
  display: flex;
  flex-direction: column;
`;

const StyledAuthorName = styled.span`
  font-size: var(--fz-md);
  font-weight: 600;
  color: var(--lightest-slate);
`;

const StyledAuthorRole = styled.span`
  font-size: var(--fz-xxs);
  font-family: var(--font-mono);
  color: var(--slate);
`;

interface TestimonialCardProps {
  quote: string;
  name: string;
  role: string;
  avatar: string;
}

const TestimonialCard: React.FC<TestimonialCardProps> = ({ quote, name, role, avatar }) => (
  <StyledCard>
    <StyledQuoteMark>&ldquo;</StyledQuoteMark>
    <StyledQuoteText>{quote}</StyledQuoteText>
    <StyledAuthor>
      <StyledAvatarWrapper>
        <StyledAvatar src={avatar} alt={name} loading="lazy" />
      </StyledAvatarWrapper>
      <StyledAuthorInfo>
        <StyledAuthorName>{name}</StyledAuthorName>
        <StyledAuthorRole>{role}</StyledAuthorRole>
      </StyledAuthorInfo>
    </StyledAuthor>
  </StyledCard>
);

const MarqueeRow: React.FC<{ items: typeof testimonials; direction: 'left' | 'right' }> = ({
  items,
  direction,
}) => (
  <StyledMarqueeRow direction={direction}>
    {/* Render twice for seamless loop */}
    {items.map((t, i) => (
      <TestimonialCard key={`a-${i}`} {...t} />
    ))}
    {items.map((t, i) => (
      <TestimonialCard key={`b-${i}`} {...t} />
    ))}
  </StyledMarqueeRow>
);

const Testimonials: React.FC = () => {
  const revealContainer = useRef<HTMLElement>(null);
  useScrollReveal(revealContainer);

  return (
    <StyledSection id="testimonials" ref={revealContainer}>
      <StyledHeading>What People Say</StyledHeading>
      <MarqueeRow items={row1} direction="left" />
      <MarqueeRow items={row2} direction="right" />
    </StyledSection>
  );
};

export default Testimonials;
