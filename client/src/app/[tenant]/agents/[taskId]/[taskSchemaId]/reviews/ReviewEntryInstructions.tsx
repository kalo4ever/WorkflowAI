import { useEffect } from 'react';
import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Textarea } from '@/components/ui/Textarea';

type ReviewEntryInstructionsProps = {
  instructions: string;
  onChange: (instructions: string) => void;
  disabled: boolean;
};

export function ReviewEntryInstructions(props: ReviewEntryInstructionsProps) {
  const { instructions, onChange, disabled } = props;

  const [comment, setComment] = useState(instructions);

  useEffect(() => {
    setComment(instructions);
  }, [instructions]);

  return (
    <div className='flex flex-col items-start gap-2 w-full h-full'>
      <Textarea
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        placeholder={'Add evaluation instructions specific to this input'}
        className='flex text-gray-900 border-gray-300 font-lato text-[13px] placeholder:text-gray-400 w-full'
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
  );
}
