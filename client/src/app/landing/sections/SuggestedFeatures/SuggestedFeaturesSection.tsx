import { cx } from 'class-variance-authority';
import { SuggestedFeatures } from './SuggestedFeatures';

type Props = {
  className?: string;
};

export function SuggestedFeaturesSection(props: Props) {
  const { className } = props;
  return (
    <div className={cx('flex items-center justify-center w-full h-full px-16', className)}>
      <div className='flex w-full max-w-[1132px] h-[820px] max-h-[820px] bg-white rounded-[4px] border border-gray-200 shadow-md overflow-hidden'>
        <SuggestedFeatures />
      </div>
    </div>
  );
}
