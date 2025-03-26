import { cx } from 'class-variance-authority';

type SchemaSplattedSectionProps = {
  title: string;
  details?: string;
  rightContent?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
};

export function SchemaSplattedSection(props: SchemaSplattedSectionProps) {
  const { title, details, rightContent, children, className, style } = props;
  return (
    <div className={cx('flex flex-col', className)} style={style}>
      <div className='flex flex-row w-full h-[64px] px-4 items-center justify-between flex-shrink-0'>
        <div className='flex flex-col items-start'>
          <div className=' text-gray-700 text-base font-semibold font-lato'>{title}</div>
          {details && <div className=' text-gray-500 text-xs font-normal font-lato text-right'>{details}</div>}
        </div>
        {!!rightContent && rightContent}
      </div>
      <div className='flex w-full border-t border-gray-200 border-dashed'>{children}</div>
    </div>
  );
}
