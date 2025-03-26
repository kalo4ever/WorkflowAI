import { ChevronUpDownFilled } from '@fluentui/react-icons';
import { TaskSchemaBadgeContainer } from '@/components/TaskSchemaBadge/TaskSchemaBadgeContainer';
import { cn } from '@/lib/utils';
import { TaskSchemaID } from '@/types/aliases';

type SchemaSectionProps = {
  taskSchemaId: TaskSchemaID;
  isSelected: boolean;
  isActive: boolean;
  showSlash?: boolean;
};

export function SchemaSection(props: SchemaSectionProps) {
  const { taskSchemaId, isSelected, isActive, showSlash = true } = props;
  return (
    <div className='flex flex-row items-center cursor-pointer'>
      <div
        className={cn(
          'flex flex-row items-center ml-3 border border-gray-200/50 rounded-[2px] py-1.5 pl-3 pr-2.5',
          isSelected
            ? 'border-gray-300 bg-gray-100 shadow-inner'
            : 'hover:border-gray-300 hover:bg-white/60 hover:shadow-sm'
        )}
      >
        <TaskSchemaBadgeContainer schemaId={taskSchemaId} isActive={isActive} />
        <ChevronUpDownFilled className='ml-2 h-4 w-4 shrink-0 text-gray-500' />
      </div>
      {showSlash && <div className='ml-3 text-[14px] font-semibold text-gray-400'>/</div>}
    </div>
  );
}
