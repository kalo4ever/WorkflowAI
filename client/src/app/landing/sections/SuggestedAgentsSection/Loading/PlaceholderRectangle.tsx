import { cx } from 'class-variance-authority';

type PlaceholderRectangleProps = {
  className?: string;
};

export function PlaceholderRectangle(props: PlaceholderRectangleProps) {
  const { className } = props;
  return (
    <div
      className={cx(
        'bg-gradient-to-r from-gray-100 to-gray-200 rounded-[2px]',
        className
      )}
    />
  );
}
