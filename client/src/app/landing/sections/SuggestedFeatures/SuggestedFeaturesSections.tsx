import { cx } from 'class-variance-authority';
import { Loader2 } from 'lucide-react';
import { FeatureSectionPreview, TagPreview } from '@/types/workflowAI';

type SuggestedFeaturesSectionsTagProps = {
  tag: TagPreview;
  selected: boolean;
  onClick: () => void;
};

function SuggestedFeaturesSectionsTag(props: SuggestedFeaturesSectionsTagProps) {
  const { tag, selected, onClick } = props;

  return (
    <div
      className={cx(
        'border-l-[2px] transition-colors duration-200 ease-in-out text-[14px] font-medium px-4 py-2 cursor-pointer hover:bg-indigo-50',
        {
          'border-transparent text-gray-700': !selected,
          'bg-indigo-50 bg-opacity-50 border-indigo-700 text-indigo-700': selected,
        }
      )}
      onClick={onClick}
    >
      {tag.name}
    </div>
  );
}

type SuggestedFeaturesSectionsProps = {
  selectedTag: TagPreview | undefined;
  setSelectedTag: (tag: TagPreview) => void;
  featureSections: FeatureSectionPreview[] | undefined;
  isLoading: boolean;
};

export function SuggestedFeaturesSections(props: SuggestedFeaturesSectionsProps) {
  const { selectedTag, setSelectedTag, featureSections, isLoading } = props;

  if (isLoading) {
    return (
      <div className='flex items-center justify-center h-full w-full'>
        <Loader2 className='h-6 w-6 animate-spin text-gray-400' />
      </div>
    );
  }

  return (
    <div className='flex flex-col gap-4 px-4 pt-[88px] w-full overflow-y-auto'>
      {featureSections?.map((featureSection) => (
        <div key={featureSection.name} className='flex flex-col w-full'>
          <div className='text-gray-400 text-[13px] font-normal px-4 py-2'>{featureSection.name}</div>
          <div className='flex flex-col w-full'>
            {featureSection.tags.map((tag) => (
              <SuggestedFeaturesSectionsTag
                key={`${featureSection.name}-${tag.name}`}
                tag={tag}
                selected={selectedTag?.name === tag.name}
                onClick={() => setSelectedTag(tag)}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
