import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Textarea } from '@/components/ui/Textarea';

type ReviewMainInstructionsProps = {
  instructions: string | undefined;
  onChange: (instructions: string) => void;
  disabled: boolean;
};

export function ReviewMainInstructions(props: ReviewMainInstructionsProps) {
  const { instructions, onChange, disabled } = props;

  const [comment, setComment] = useState(instructions);

  useEffect(() => {
    setComment(instructions);
  }, [instructions]);

  return (
    <div className='flex flex-col gap-1'>
      <div className='text-[13px] font-medium text-gray-900'>
        Evaluation Instructions
      </div>
      <div className='flex flex-col justify-center gap-2'>
        <Textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder={'Add general evaluation instructions for all runs'}
          className='text-gray-900 border-gray-300 font-lato text-[13px] placeholder:text-gray-400'
          disabled={disabled}
        />
        {comment !== instructions && (
          <Button
            variant='newDesign'
            size='none'
            onClick={() => onChange(comment ?? '')}
            className='w-fit px-2 py-1.5 font-semibold text-xs'
            disabled={disabled}
          >
            Save
          </Button>
        )}
      </div>
    </div>
  );
}
