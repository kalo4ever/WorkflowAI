import {
  HoverCardContent,
  HoverCardContentProps,
} from '@radix-ui/react-hover-card';
import { Info } from 'lucide-react';
import { useCallback, useEffect, useRef } from 'react';
import { DebouncedState } from 'usehooks-ts';
import { TaskVersionNotesInput } from '@/components/TaskVersionNotesInput';
import { Button } from '@/components/ui/Button';

type AddNoteCardProps = {
  versionId: string | null | undefined;
  notes: string | null | undefined;
  handleUpdateNotes: DebouncedState<
    (versionId: string, notes: string) => Promise<void>
  >;
  closeNoteHoverCard: () => void;
  side?: HoverCardContentProps['side'];
  align?: HoverCardContentProps['align'];
};

export function AddNoteCard(props: AddNoteCardProps) {
  const {
    versionId,
    notes,
    handleUpdateNotes,
    closeNoteHoverCard,
    side,
    align,
  } = props;

  const noteHoverCardRef = useRef<HTMLDivElement>(null);

  const handleClickOutside = useCallback(
    (event: MouseEvent) => {
      if (
        !!noteHoverCardRef.current &&
        !noteHoverCardRef.current.contains(event.target as Node)
      ) {
        closeNoteHoverCard();
      }
    },
    [closeNoteHoverCard]
  );

  useEffect(() => {
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [handleClickOutside]);

  const onClose = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      closeNoteHoverCard();
    },
    [closeNoteHoverCard]
  );

  const onUpdateNotes = useCallback(
    (notes: string) => {
      if (!versionId) {
        return;
      }
      handleUpdateNotes(versionId, notes);
    },
    [versionId, handleUpdateNotes]
  );

  return (
    <HoverCardContent
      className='w-fit min-w-[340px] max-w-[660px] h-fit p-0 bg-white overflow-hidden rounded-[2px] border border-gray-200 shadow-md z-[100] animate-in fade-in-0 zoom-in-95'
      side={side}
      align={align}
    >
      <div className='bg-white font-lato' ref={noteHoverCardRef}>
        <div className='flex items-center justify-between border-b border-gray-200 border-dashed px-4 py-4'>
          <div className='text-gray-900 text-sm font-medium'>Add Note</div>
          <Button variant='newDesign' onClick={onClose}>
            Done
          </Button>
        </div>
        <div className='flex flex-col gap-4 px-4 py-4'>
          <TaskVersionNotesInput
            versionId={versionId}
            notes={notes}
            onUpdateNotes={onUpdateNotes}
          />
          <div className='flex items-center gap-1 text-gray-500 text-xs font-normal'>
            <Info size={16} className='text-purple-600' />
            Any notes you add are automatically saved
          </div>
        </div>
      </div>
    </HoverCardContent>
  );
}
