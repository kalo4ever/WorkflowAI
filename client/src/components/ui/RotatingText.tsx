import { useEffect, useState } from 'react';

type RotatingTextProps = {
  firstText: string;
  secondText: string;
};

export function RotatingText(props: RotatingTextProps) {
  const { firstText, secondText } = props;

  const [isFirstTextVisible, setIsFirstTextVisible] = useState(true);

  useEffect(() => {
    const interval = setInterval(() => {
      setIsFirstTextVisible((prevVisible) => !prevVisible);
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  // We are not using Tailwind CSS here becasue of wrong safari behavioir when fading out (fading in works)
  return (
    <div className='grid place-items-center h-auto'>
      <div
        className='flex justify-center items-start'
        style={{
          gridArea: '1 / 1',
          opacity: isFirstTextVisible ? 1 : 0,
          transition: 'opacity 0.5s ease-in-out',
          willChange: 'opacity',
        }}
      >
        {firstText}
      </div>
      <div
        className='flex justify-center items-start'
        style={{
          gridArea: '1 / 1',
          opacity: isFirstTextVisible ? 0 : 1,
          transition: 'opacity 0.5s ease-in-out',
          willChange: 'opacity',
        }}
      >
        {secondText}
      </div>
    </div>
  );
}
