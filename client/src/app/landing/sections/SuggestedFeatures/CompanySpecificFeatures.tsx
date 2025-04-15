import { capitalize } from 'lodash';
import { useMemo } from 'react';
import { TagPreview } from '@/types/workflowAI/models';
import { SuggestedFeaturesList } from './SuggestedFeaturesList';
import { SuggestedFeaturesSearch } from './SuggestedFeaturesSearch';

type CompanySpecificFeaturesProps = {
  companyURL?: string;
  setCompanyURL?: (companyURL: string) => void;
};

export function CompanySpecificFeatures(props: CompanySpecificFeaturesProps) {
  const { companyURL, setCompanyURL } = props;

  const tag: TagPreview = useMemo(() => {
    return {
      name: capitalize(companyURL),
      kind: 'company_specific',
    };
  }, [companyURL]);

  return (
    <div className='flex flex-row h-full w-full overflow-hidden'>
      <div className='flex flex-col flex-1 h-full overflow-hidden'>
        <div className='flex px-6 sm:px-16 py-6 sm:py-10 border-b border-gray-100'>
          <div className='flex flex-col gap-4 w-full sm:items-start items-center'>
            <div className='text-[18px] text-gray-500 font-normal'>
              What Al features would make your users say <span className='font-semibold'>&apos;wow&apos;</span>?
            </div>
            <SuggestedFeaturesSearch companyURL={companyURL} setCompanyURL={setCompanyURL} />
          </div>
        </div>
        <SuggestedFeaturesList tag={tag} companyURL={companyURL} />
      </div>
    </div>
  );
}
