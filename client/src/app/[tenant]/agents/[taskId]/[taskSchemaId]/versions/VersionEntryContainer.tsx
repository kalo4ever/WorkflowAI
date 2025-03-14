import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import { TaskID } from '@/types/aliases';
import { TenantID } from '@/types/aliases';
import { TaskSchemaID } from '@/types/aliases';
import { VersionEntryContainerHeader } from './VersionEntryContainerHeader';
import { VersionEntryContainerProperties } from './VersionEntryContainerProperties';
import { VersionEntryContainerVersions } from './VersionEntryContainerVersions';
import { VersionInputOutputSchemas } from './VersionInputOutputSchemas';
import { VersionEntry } from './utils';

// Initialize the relative time plugin
dayjs.extend(relativeTime);

type VersionEntryContainerProps = {
  entry: VersionEntry;
  previousEntry: VersionEntry | undefined;
  isLatest: boolean;
  tenant: TenantID;
  taskId: TaskID;
  taskSchemaId: TaskSchemaID;
  openSchemasByDefault: boolean;
};

export function VersionEntryContainer(props: VersionEntryContainerProps) {
  const {
    entry,
    previousEntry,
    isLatest,
    tenant,
    taskId,
    taskSchemaId,
    openSchemasByDefault,
  } = props;

  return (
    <div className='flex flex-col w-full h-max border-gray-200 border rounded-[2px]'>
      <VersionEntryContainerHeader
        entry={entry}
        previousEntry={previousEntry}
        isLatest={isLatest}
      />

      <div className='flex flex-row'>
        <div className='flex w-[438px] flex-shrink-0'>
          <VersionEntryContainerVersions
            entry={entry}
            tenant={tenant}
            taskId={taskId}
            taskSchemaId={taskSchemaId}
          />
        </div>
        <VersionEntryContainerProperties entry={entry} />
      </div>

      <VersionInputOutputSchemas
        tenant={tenant}
        taskId={taskId}
        entry={entry}
        openSchemasByDefault={openSchemasByDefault}
      />
    </div>
  );
}
