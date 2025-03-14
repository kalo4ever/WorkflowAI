import { Archive16Regular } from '@fluentui/react-icons';
import { TaskSchemaID } from '@/types/aliases';
import { SchemaCell } from './schemasContent';

type SchemasSelectorProps = {
  schemaIds: TaskSchemaID[];
  archivedSchemasIds: TaskSchemaID[];
  activeSchemasIds: TaskSchemaID[];
  currentSchemaId: TaskSchemaID;
  onSelect: (schemaId: TaskSchemaID) => void;
};

export function SchemasSelector(props: SchemasSelectorProps) {
  const {
    schemaIds,
    archivedSchemasIds,
    activeSchemasIds,
    currentSchemaId,
    onSelect,
  } = props;

  return (
    <div className='flex flex-col shrink-0 w-[200px] h-full border-r border-gray-200 border-dashed'>
      <div className='px-4 h-[48px] border-b border-gray-200 border-dashed text-gray-700 text-[16px] font-semibold flex items-center shrink-0'>
        Schemas
      </div>
      <div className='flex flex-col w-full h-full overflow-auto'>
        <div className='flex flex-col w-full p-2'>
          {schemaIds.map((schemaId) => (
            <SchemaCell
              key={schemaId}
              schemaId={schemaId}
              isSelected={schemaId === currentSchemaId}
              onSelect={onSelect}
              isActive={activeSchemasIds.includes(schemaId)}
            />
          ))}
        </div>

        {archivedSchemasIds.length > 0 && (
          <>
            <div className='text-gray-500 text-[13px] font-semibold border-t border-gray-200 border-dashed pt-3 pb-2 px-3 flex items-center gap-2'>
              <Archive16Regular />
              Archived
            </div>
            <div className='flex flex-col w-full px-2'>
              {archivedSchemasIds.map((schemaId) => (
                <SchemaCell
                  key={schemaId}
                  schemaId={schemaId}
                  isSelected={schemaId === currentSchemaId}
                  onSelect={onSelect}
                  isActive={activeSchemasIds.includes(schemaId)}
                />
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
