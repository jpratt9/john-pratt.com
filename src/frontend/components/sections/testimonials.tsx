import React, { useRef } from 'react';
import styled, { keyframes } from 'styled-components';
import { useScrollReveal } from '@hooks';
import { media } from '@styles';
import meghAvatar from '@images/testimonials/megh.jpeg';
import neilAvatar from '@images/testimonials/neil.png';
import dustinAvatar from '@images/testimonials/dustin.jpg';

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
    role: 'Student',
    avatar: 'https://i.pravatar.cc/80?img=12',
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

const StyledAvatar = styled.img`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
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
      <StyledAvatar src={avatar} alt={name} loading="lazy" />
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
