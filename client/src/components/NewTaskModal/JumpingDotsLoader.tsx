import { cx } from 'class-variance-authority';

type JumpingDotsLoaderProps = {
  className?: string;
};

export function JumpingDotsLoader(props: JumpingDotsLoaderProps) {
  const { className } = props;

  return (
    <div
      className={cx(
        'w-fit h-10 flex justify-center items-center space-x-2',
        className
      )}
    >
      <div className='w-2 h-2 bg-gray-800 rounded-full animate-jump1'></div>
      <div className='w-2 h-2 bg-gray-800 rounded-full animate-jump2'></div>
      <div className='w-2 h-2 bg-gray-800 rounded-full animate-jump3'></div>
    </div>
  );
}
