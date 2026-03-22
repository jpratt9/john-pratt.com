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
import angelaAvatar from '@images/testimonials/angela.jpeg';

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
      'He knows his stuff across the stack, and brings good technical and business insight to the table.',
    name: 'Neil Chainani',
    role: 'Software Developer, CDC',
    avatar: neilAvatar,
  },
  {
    quote:
      'Fast turnaround with all the features I needed - he built my website so I could reach more clients and charge more for my services. You can tell he prioritizes customer satisfaction.',
    name: 'Dustin Lewis',
    role: 'English Tutor @ Preply',
    avatar: dustinAvatar,
  },
  {
    quote:
      'John has been a great coach for me. He\'s helped me improve my confidence and networking skills, and opened my eyes to things I didn\'t realize were important.',
    name: 'Andrew Lackey',
    role: 'Student, University of North Carolina at Charlotte',
    avatar: lackeyAvatar,
  },
  {
    quote:
      'John was my TDP mentor when I joined Capital One. He readily offered career advice and helped me get up to speed quickly with company culture.',
    name: 'Rohan Upponi',
    role: 'Software Engineer, Capital One',
    avatar: rohanAvatar,
  },
  {
    quote:
      'John was my TDP mentor during my Capital One internship. His biweekly check-ins kept me on track and were a major reason I received a full-time offer.',
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
      'John was my TDP buddy during my internship at Capital One. He advocated for me and helped me switch to a project better aligned with my skills.',
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
      'John was our Tech Lead through Pratt Solutions where we rebuilt a Python aerospace app from scratch. He brought in automated testing, CI/CD, and scalable engineering practices that elevated the entire team.',
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
  {
    quote:
      'John built me a professional portfolio site as a birthday gift — it turned out amazing and really captures my work in biophysical research.',
    name: 'Angela Develin, Ph.D.',
    role: 'Post Doctoral Fellow, Boehringer Ingelheim',
    avatar: angelaAvatar,
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
  align-items: center;
  gap: 28px;
  width: max-content;
  animation: ${({ direction }) => (direction === 'left' ? scrollLeft : scrollRight)}
    40s linear infinite;
  margin-bottom: 28px;

  &:hover {
    animation-play-state: paused;
  }

  ${media.tablet} {
    gap: 20px;
    margin-bottom: 20px;
    animation-duration: 30s;
  }
`;

const StyledCard = styled.div`
  flex-shrink: 0;
  width: 360px;
  background-color: var(--light-navy);
  border-radius: 12px;
  padding: 32px;
  font-family: var(--font-sans);
  transition: var(--transition);
  box-shadow: 0 10px 30px -15px var(--navy-shadow);

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 30px -15px var(--navy-shadow);
  }

  ${media.desktop} {
    width: 320px;
    padding: 28px;
  }
  ${media.mobile} {
    width: 280px;
    padding: 24px;
  }
`;

const StyledQuoteMark = styled.span`
  font-family: Georgia, serif;
  font-size: 40px;
  line-height: 0.5;
  color: var(--green);
  display: block;
  margin-bottom: 14px;
  opacity: 0.8;
`;

const StyledQuoteText = styled.p`
  font-size: var(--fz-md);
  color: var(--light-slate);
  line-height: 1.7;
  padding-bottom: 14px;
`;

const StyledAuthor = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 14px;
  border-top: 1px solid var(--lightest-navy);
`;

const StyledAvatarWrapper = styled.div`
  width: 44px;
  height: 44px;
  min-width: 44px;
  border-radius: 50%;
  overflow: hidden;
  background-color: var(--light-navy);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid var(--lightest-navy);
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
