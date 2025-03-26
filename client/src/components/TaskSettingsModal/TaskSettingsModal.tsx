import { useRouter } from 'next/navigation';
import { useCallback, useEffect, useState } from 'react';
import { AlertDialog } from '@/components/ui/AlertDialog';
import { Dialog, DialogContent } from '@/components/ui/Dialog';
import { displaySuccessToaster } from '@/components/ui/Sonner';
import { TASK_SETTINGS_MODAL_OPEN, useQueryParamModal } from '@/lib/globalModal';
import { useTaskSchemaParams } from '@/lib/hooks/useTaskParams';
import { tasksRoute } from '@/lib/routeFormatter';
import { useOrFetchTask, useTasks } from '@/store';
import { useApiKeysModal } from '../ApiKeysModal/ApiKeysModal';
import { GeneralSettingsContent } from './GeneralSettingsContent';
import { SettingsSidebar } from './SettingsSidebar';

export function TaskSettingsModal() {
  const { taskId, tenant } = useTaskSchemaParams();
  const { task } = useOrFetchTask(tenant, taskId);

  const [deleteConfirmModalOpen, setDeleteConfirmModal] = useState(false);
  const [visibilityConfirmModalOpen, setVisibilityConfirmModal] = useState(false);
  const [currentTaskName, setCurrentTaskName] = useState<string>('');

  const { open, closeModal: onClose } = useQueryParamModal(TASK_SETTINGS_MODAL_OPEN);

  const { push } = useRouter();
  const updateTask = useTasks((state) => state.updateTask);
  const deleteTask = useTasks((state) => state.deleteTask);

  const handleDeleteTask = useCallback(async () => {
    await deleteTask(tenant, taskId);
    setDeleteConfirmModal(false);
    onClose();
    push(tasksRoute(tenant));
  }, [deleteTask, push, taskId, tenant, setDeleteConfirmModal, onClose]);

  const handleRenameTask = useCallback(
    async (newTaskName: string) => {
      await updateTask(tenant, taskId, {
        name: newTaskName,
      });
      displaySuccessToaster('AI agent renamed');
    },
    [taskId, tenant, updateTask]
  );

  useEffect(() => {
    if (!open || !task?.name) return;
    setCurrentTaskName(task?.name);
  }, [task?.name, open]);

  const onTaskNameChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setCurrentTaskName(e.target.value);
  }, []);

  const onRenameTask = useCallback(async () => {
    await handleRenameTask(currentTaskName);
  }, [currentTaskName, handleRenameTask]);

  const renameDisabled = currentTaskName === task?.name;

  const toggleTaskVisibility = useCallback(async () => {
    if (!task) return;
    await updateTask(tenant, taskId, {
      is_public: !task.is_public,
    });
    setVisibilityConfirmModal(false);
  }, [task, taskId, tenant, updateTask, setVisibilityConfirmModal]);

  const { open: manageApiKeysOpen, openModal: openManageApiKeysModal } = useApiKeysModal();
  const onOpenManageApiKeys = useCallback(() => {
    openManageApiKeysModal();
  }, [openManageApiKeysModal]);
  useEffect(() => {
    // We wait for the manage api keys modal to open before closing the task settings modal
    // To avoid a race condition between the 2 redirects
    if (manageApiKeysOpen) {
      onClose();
    }
  }, [manageApiKeysOpen, onClose]);

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className='p-0 max-w-fit'>
        <div className='flex h-[450px]'>
          <SettingsSidebar onOpenManageApiKeys={onOpenManageApiKeys} />
          <GeneralSettingsContent
            task={task}
            onClose={onClose}
            onRenameTask={onRenameTask}
            onTaskNameChange={onTaskNameChange}
            renameDisabled={renameDisabled}
            currentTaskName={currentTaskName}
            setVisibilityConfirmModal={setVisibilityConfirmModal}
            setDeleteConfirmModal={setDeleteConfirmModal}
          />
        </div>
      </DialogContent>
      <AlertDialog
        open={deleteConfirmModalOpen}
        title={'Delete this task?'}
        subTitle='Are you sure you want to delete this AI agent?'
        text='It will be gone forever and you won’t be able to recover it.'
        confrimationText='Delete'
        onCancel={() => setDeleteConfirmModal(false)}
        onConfirm={handleDeleteTask}
        destructive
      />
      <AlertDialog
        open={visibilityConfirmModalOpen}
        title={`Make AI Agent ${!!task?.is_public ? 'Private' : 'Public'}?`}
        subTitle={
          !!task?.is_public
            ? 'You will no longer be able to share your AI agent with people outside of your organization'
            : 'This will mean anyone can view your AI agent including previous task runs.'
        }
        text={`You can always set your AI agent to be ${!!task?.is_public ? 'public' : 'private'} again.`}
        confrimationText='Confirm'
        onCancel={() => setVisibilityConfirmModal(false)}
        onConfirm={toggleTaskVisibility}
      />
    </Dialog>
  );
}
