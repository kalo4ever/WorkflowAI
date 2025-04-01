import { cx } from 'class-variance-authority';
import { SuggestedFeatures } from './SuggestedFeatures';

type Props = {
  className?: string;
  companyURL?: string;
};

export function SuggestedFeaturesSection(props: Props) {
  const { className, companyURL } = props;
  return (
    <div className={cx('flex items-center justify-center w-full h-max px-4 sm:px-16', className)}>
      <div className='flex w-full max-w-[1132px] sm:h-[820px] h-max sm:max-h-[820px] max-h-max bg-white rounded-[4px] border border-gray-200 shadow-md overflow-hidden'>
        <SuggestedFeatures companyURL={companyURL} />
      </div>
    </div>
  );
}
