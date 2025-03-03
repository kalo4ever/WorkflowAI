import { TaskVersionsContainer } from '@/components/v2/TaskVersions/TaskVersionsContainer';
import { VersionAvatarType } from '@/components/v2/TaskVersions/utils';
import { TaskSchemaID } from '@/types/aliases';
import { TenantID } from '@/types/aliases';
import { TaskID } from '@/types/aliases';
import { VersionEntryContainerChangelog } from './VersionEntryContainerChangelog';
import { VersionEntry } from './utils';

type VersionEntryContainerVersionsProps = {
  entry: VersionEntry;
  tenant: TenantID;
  taskId: TaskID;
  taskSchemaId: TaskSchemaID;
};

export function VersionEntryContainerVersions(
  props: VersionEntryContainerVersionsProps
) {
  const { entry, tenant, taskId, taskSchemaId } = props;

  return (
    <div className='flex flex-col w-full h-max px-4 py-3 gap-4'>
      <VersionEntryContainerChangelog entry={entry} />
      <TaskVersionsContainer
        tenant={tenant}
        taskId={taskId}
        taskSchemaId={taskSchemaId}
        avatarType={VersionAvatarType.Created}
        areVersionsInitialized={true}
        versionsToShow={entry.versions}
        showHeader={true}
        showGroupActions={true}
        smallMode={true}
        sort='version'
      />
    </div>
  );
}
