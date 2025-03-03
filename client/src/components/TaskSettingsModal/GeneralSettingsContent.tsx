import { X } from 'lucide-react';
import { SerializableTask } from '@/types/workflowAI';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';

type DangerZoneCellProps = {
  title: string;
  subtitle: string;
  onClick: () => void;
};

function DangerZoneCell(props: DangerZoneCellProps) {
  const { title, subtitle, onClick } = props;
  return (
    <div className='gap-4 flex items-center justify-between'>
      <div className='mr-2'>
        <div className='text-slate-600 text-sm font-medium'>{title}</div>
        <div className='text-slate-600 text-sm'>{subtitle}</div>
      </div>
      <Button variant='destructive' onClick={onClick}>
        {title}
      </Button>
    </div>
  );
}

type GeneralSettingsContentProps = {
  task: SerializableTask | undefined;
  onClose: () => void;
  onRenameTask: () => void;
  onTaskNameChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  renameDisabled: boolean;
  currentTaskName: string;
  setVisibilityConfirmModal: (open: boolean) => void;
  setDeleteConfirmModal: (open: boolean) => void;
};

export function GeneralSettingsContent(props: GeneralSettingsContentProps) {
  const {
    task,
    onClose,
    onRenameTask,
    onTaskNameChange,
    renameDisabled,
    currentTaskName,
    setVisibilityConfirmModal,
    setDeleteConfirmModal,
  } = props;
  return (
    <div className='w-[530px] px-6 py-4 flex flex-col'>
      <div className='flex items-center justify-between w-full border-b pb-4'>
        <div className='text-slate-900 text-lg font-medium'>General</div>
        <Button
          lucideIcon={X}
          variant='ghost'
          onClick={onClose}
          className='text-slate-500'
        />
      </div>
      <div className='py-4 flex flex-col gap-4 text-slate-700 text-sm'>
        <div>AI Agent Name</div>
        <div className='pl-4 py-2 pr-8 gap-[34px] flex items-center'>
          <Input value={currentTaskName} onChange={onTaskNameChange} />
          <Button disabled={renameDisabled} onClick={onRenameTask}>
            Rename
          </Button>
        </div>
        <div>Danger Zone</div>
        <div className='px-4'>
          <div className='border border-red-200 rounded-lg px-4 py-4 flex flex-col gap-7'>
            <DangerZoneCell
              title='Change AI Agent Visibility'
              subtitle={`This AI Agent is currently ${!!task?.is_public ? 'public' : 'private'}`}
              onClick={() => setVisibilityConfirmModal(true)}
            />
            <DangerZoneCell
              title='Delete AI Agent'
              subtitle='Once you delete a AI agent, it will be gone forever'
              onClick={() => setDeleteConfirmModal(true)}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
