import { ChevronDownRegular } from '@fluentui/react-icons';
import { useState } from 'react';
import { cn } from '@/lib/utils';
import { TaskID } from '@/types/aliases';
import { TenantID } from '@/types/aliases';
import { InputOutputSchemas } from './InputOutputSchamas';
import { VersionEntry } from './utils';

type VersionInputOutputSchemasProps = {
  tenant: TenantID;
  taskId: TaskID;
  entry: VersionEntry;
  openSchemasByDefault: boolean;
};

export function VersionInputOutputSchemas(
  props: VersionInputOutputSchemasProps
) {
  const { tenant, taskId, entry, openSchemasByDefault } = props;

  const [isOpen, setIsOpen] = useState(openSchemasByDefault);

  return (
    <div className='flex flex-col w-full h-max'>
      <div
        className={cn(
          'flex flex-row w-full h-[44px] border-t border-gray-200 justify-between items-center px-4 cursor-pointer',
          isOpen && 'border-b border-gray-200'
        )}
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className='text-gray-700 text-[13px] font-semibold'>
          Description and Examples
        </div>

        <ChevronDownRegular
          className={cn('h-4 w-4 text-gray-700', isOpen && 'rotate-180')}
        />
      </div>
      {!!entry.versions[0].id && isOpen && (
        <div className='flex h-max w-full p-4'>
          <InputOutputSchemas
            tenant={tenant}
            taskId={taskId}
            versionId={entry.versions[0].id}
          />
        </div>
      )}
    </div>
  );
}
