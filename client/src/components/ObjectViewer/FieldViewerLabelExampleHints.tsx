import { cx } from 'class-variance-authority';
import { useMemo, useState } from 'react';

type FieldViewerLabelExampleHintsProps = {
  description: string | undefined;
  examples: unknown[] | undefined;
  onClick?: () => void;
};

export function FieldViewerLabelExampleHints(
  props: FieldViewerLabelExampleHintsProps
) {
  const { description, examples, onClick } = props;

  const supportedExamples = useMemo(() => {
    if (!examples) {
      return undefined;
    }

    const filteredExamples = examples.filter(
      (example) => typeof example === 'string'
    ) as string[];

    return filteredExamples.length ? filteredExamples : undefined;
  }, [examples]);

  const [isHovering, setIsHovering] = useState(false);
  const shouldShowEditBadge = isHovering && !!onClick;

  return (
    <div
      className={cx(
        'flex flex-col gap-3 py-3 bg-white relative',
        !!onClick && 'cursor-pointer'
      )}
      onClick={onClick}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      {!!description ? (
        <div className='flex flex-row px-3'>
          <div className='text-[13px] text-gray-600 font-medium pt-[5px] min-w-[100px]'>
            description:
          </div>
          <div className='text-[13px] text-gray-900 font-normal bg-gray-100 rounded-[2px] border border-gray-200 px-2 py-1 max-w-[350px]'>
            {description}
          </div>
        </div>
      ) : (
        <div className='flex flex-row px-3'>
          <div className='text-[13px] text-gray-600 font-medium min-w-[90px]'>
            No Description
          </div>
        </div>
      )}

      {!!supportedExamples && (
        <div className='flex flex-row px-3'>
          <div className='text-[13px] text-gray-600 font-medium pt-1.5 min-w-[100px] max-w-[300px]'>
            examples:
          </div>
          <div className='flex flex-wrap gap-1 px-1 py-1 bg-white border border-gray-200 rounded-[2px]'>
            {supportedExamples.map((example) => (
              <div
                key={example}
                className='text-[13px] text-gray-900 font-normal bg-gray-100 rounded-[2px] border px-1'
              >
                {example}
              </div>
            ))}
          </div>
        </div>
      )}

      {shouldShowEditBadge && (
        <div className='absolute -top-4 right-2 px-3 py-1.5 text-[13px] font-normal text-white bg-gray-700 border border-gray-200 rounded-[3px]'>
          Edit
        </div>
      )}
    </div>
  );
}
