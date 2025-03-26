import Image from 'next/image';
import LogoSrc from '@/components/Images/Logo.png';

type WorkflowAILogoProps = {
  ratio?: number;
  className?: string;
};

export function WorkflowAIIcon(props: WorkflowAILogoProps) {
  const { ratio = 1, className = '' } = props;
  const width = 16 * ratio;
  const height = 16 * ratio;
  return (
    <svg
      width={width}
      height={height}
      className={className}
      viewBox='0 0 16 16'
      fill='none'
      xmlns='http://www.w3.org/2000/svg'
    >
      <defs>
        <linearGradient id='workflowGradient' x1='0%' y1='0%' x2='100%' y2='0%'>
          <stop offset='0%' stopColor='#8759E3' />
          <stop offset='100%' stopColor='#4235F8' />
        </linearGradient>
      </defs>
      <path
        id='Subtract'
        fillRule='evenodd'
        clipRule='evenodd'
        d='M3.2 0C1.43269 0 0 1.43269 0 3.2V12.8C0 14.5673 1.43269 16 3.2 16H12.8C14.5673 16 16 14.5673 16 12.8V3.2C16 1.43269 14.5673 0 12.8 0H3.2ZM8 12C10.2091 12 12 10.2091 12 8C12 5.79086 10.2091 4 8 4C5.79086 4 4 5.79086 4 8C4 10.2091 5.79086 12 8 12Z'
        fill='url(#workflowGradient)'
      />
    </svg>
  );
}

export function WorkflowAIIconWithCurrentColor(props: WorkflowAILogoProps) {
  const { ratio = 1, className = '' } = props;
  const width = 16 * ratio;
  const height = 16 * ratio;
  return (
    <svg
      width={width}
      height={height}
      className={className}
      viewBox='0 0 16 16'
      fill='none'
      xmlns='http://www.w3.org/2000/svg'
    >
      <path
        id='Subtract'
        fillRule='evenodd'
        clipRule='evenodd'
        d='M3.2 0C1.43269 0 0 1.43269 0 3.2V12.8C0 14.5673 1.43269 16 3.2 16H12.8C14.5673 16 16 14.5673 16 12.8V3.2C16 1.43269 14.5673 0 12.8 0H3.2ZM8 12C10.2091 12 12 10.2091 12 8C12 5.79086 10.2091 4 8 4C5.79086 4 4 5.79086 4 8C4 10.2091 5.79086 12 8 12Z'
        fill='currentColor'
      />
    </svg>
  );
}

export function WorkflowAIGradientIcon(props: WorkflowAILogoProps) {
  const { ratio = 1, className = '' } = props;
  const width = 16 * ratio;
  const height = 16 * ratio;
  return <Image src={LogoSrc} width={width} height={height} className={className} alt='Workflow AI Logo' priority />;
}
