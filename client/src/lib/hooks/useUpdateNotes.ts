import { useCallback } from 'react';
import { useDebounceCallback } from 'usehooks-ts';
import { useIsAllowed } from '@/lib/hooks/useIsAllowed';
import { useVersions } from '@/store/versions';
import { TaskID, TenantID } from '@/types/aliases';

type Props = {
  tenant: TenantID | undefined;
  taskId: TaskID;
};

export function useUpdateNotes(props: Props) {
  const { tenant, taskId } = props;
  const { checkIfAllowed } = useIsAllowed();

  const updateNote = useVersions((state) => state.updateNote);

  const handleUpdateNotes = useDebounceCallback(
    useCallback(
      async (versionId: string, notes: string) => {
        if (!checkIfAllowed() || !tenant) {
          return;
        }
        await updateNote(tenant, taskId, versionId, notes);
      },
      [updateNote, tenant, taskId, checkIfAllowed]
    ),
    1000
  );

  return { handleUpdateNotes };
}
