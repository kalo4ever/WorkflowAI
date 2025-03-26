import { cx } from 'class-variance-authority';

type PlaceholderRectangleProps = {
  className?: string;
};

export function PlaceholderRectangle(props: PlaceholderRectangleProps) {
  const { className } = props;
  return <div className={cx('bg-gradient-to-r from-gray-100 to-gray-200 rounded-[2px]', className)} />;
}

type GhostLoadingProps = {
  className?: string;
};

export function GhostLoading(props: GhostLoadingProps) {
  const { className } = props;

  return (
    <div className={cx('flex flex-col w-full animate-pulse gap-1.5', className)}>
      <PlaceholderRectangle className='w-full h-[14px]' />
      <PlaceholderRectangle className='w-full h-[14px]' />
    </div>
  );
}
