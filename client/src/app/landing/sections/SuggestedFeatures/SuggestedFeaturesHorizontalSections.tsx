import { cx } from 'class-variance-authority';
import { Loader2 } from 'lucide-react';
import { useMemo } from 'react';
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
        'transition-colors duration-200 ease-in-out text-[13px] font-semibold px-4 py-2 cursor-pointer shrink-0 rounded-[2px]',
        {
          'bg-gray-100 text-gray-800 hover:bg-gray-200': !selected,
          'bg-gray-800 text-gray-50 hover:bg-gray-700': selected,
        }
      )}
      onClick={onClick}
    >
      {tag.name}
    </div>
  );
}

type SuggestedFeaturesHorizontalSectionsProps = {
  selectedTag: TagPreview | undefined;
  setSelectedTag: (tag: TagPreview) => void;
  featureSections: FeatureSectionPreview[] | undefined;
  isLoading: boolean;
};

export function SuggestedFeaturesHorizontalSections(props: SuggestedFeaturesHorizontalSectionsProps) {
  const { selectedTag, setSelectedTag, featureSections, isLoading } = props;

  const tags = useMemo(() => {
    return featureSections?.flatMap((featureSection) => featureSection.tags);
  }, [featureSections]);

  if (isLoading) {
    return (
      <div className='flex items-center justify-center h-[36px] w-full'>
        <Loader2 className='h-6 w-6 animate-spin text-gray-400' />
      </div>
    );
  }

  return (
    <div className='flex flex-row gap-2 px-6 flex-1 overflow-x-auto scrollbar-hide'>
      {tags?.map((tag) => (
        <SuggestedFeaturesSectionsTag
          key={`${tag.name}`}
          tag={tag}
          selected={selectedTag?.name === tag.name}
          onClick={() => setSelectedTag(tag)}
        />
      ))}
    </div>
  );
}
