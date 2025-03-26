import { ThumbLikeRegular } from '@fluentui/react-icons';
import { ThumbDislikeRegular } from '@fluentui/react-icons';
import { useState } from 'react';
import { TaskOutputViewer } from '@/components/ObjectViewer/TaskOutputViewer';
import { Button } from '@/components/ui/Button';
import { SerializableTaskIOWithSchema } from '@/types/task';

type ReviewInputOutputEntryProps = {
  value: Record<string, unknown>;
  schema: SerializableTaskIOWithSchema | undefined;
  index: number;
  isCorrect: boolean;
  onCorrectChange: (value: Record<string, unknown>, isCorrect: boolean) => void;
  isInDemoMode: boolean;
};

export function ReviewInputOutputEntry(props: ReviewInputOutputEntryProps) {
  const { value, schema, index, isCorrect, onCorrectChange, isInDemoMode } = props;
  const [isHovering, setIsHovering] = useState(false);

  return (
    <div
      className='flex flex-col h-max w-full border border-gray-200 rounded-[2px]'
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      <div className='flex flex-row justify-between items-center w-full pl-3 pr-2 h-[44px] border-b border-gray-200 border-dashed bg-gradient-to-b from-[#F8FAFC] to-[#F8FAFC]'>
        <div className='text-[13px] font-medium text-gray-900'>
          {isCorrect ? 'Accurate' : 'Inaccurate'} #{index + 1}
        </div>
        {isHovering && (
          <Button
            variant='newDesign'
            size='sm'
            icon={
              isCorrect ? (
                <ThumbDislikeRegular className='w-[14px] h-[14px] text-gray-900' />
              ) : (
                <ThumbLikeRegular className='w-[14px] h-[14px] text-gray-900' />
              )
            }
            onClick={() => onCorrectChange(value, !isCorrect)}
            disabled={isInDemoMode}
          >
            {isCorrect ? 'Mark as Incorrect' : 'Mark as Correct'}
          </Button>
        )}
      </div>
      <TaskOutputViewer
        value={value}
        noOverflow
        schema={schema?.json_schema}
        defs={schema?.json_schema?.$defs}
        className='max-h-[400px] w-full overflow-y-auto'
        errorsByKeypath={undefined}
      />
    </div>
  );
}
