import { useCallback, useEffect, useState } from 'react';
import { usePrevious } from '@/lib/hooks';
import { Textarea } from './ui/Textarea';

export type TaskVersionNotesInputProps = {
  versionId?: string | null | undefined;
  notes: string | null | undefined;
  onUpdateNotes?: (notes: string) => void;
};

export function TaskVersionNotesInput(props: TaskVersionNotesInputProps) {
  const { versionId, notes, onUpdateNotes } = props;

  const [editedNotes, setEditedNotes] = useState(notes || '');

  const onChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      const newValue = e.target.value;
      setEditedNotes(newValue);
      onUpdateNotes?.(newValue);
    },
    [onUpdateNotes]
  );

  const previousVersionId = usePrevious(versionId);
  useEffect(() => {
    if (!versionId || !previousVersionId || versionId === previousVersionId) {
      return;
    }
    setEditedNotes(notes || '');
  }, [notes, versionId, previousVersionId]);

  const onClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
  }, []);

  return (
    <div className='w-full'>
      <Textarea
        value={editedNotes}
        onChange={onChange}
        onClick={onClick}
        placeholder='Add anything you’d like to make note of about this version...'
        className='text-gray-800 h-[120px] font-lato border-gray-200'
        autoFocus
        autoResize={false}
      />
    </div>
  );
}
