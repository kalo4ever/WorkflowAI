import { TaskTemperatureView } from '@/components/v2/TaskTemperatureBadge';
import { useCopy } from '@/lib/hooks/useCopy';
import { InstructionTooltip } from './InstructionTooltip';
import { VersionEntry } from './utils';

type VersionEntryContainerPropertiesProps = {
  entry: VersionEntry;
};

export function VersionEntryContainerProperties(
  props: VersionEntryContainerPropertiesProps
) {
  const { entry } = props;

  const onCopy = useCopy();

  return (
    <div className='flex flex-col flex-1 border-l border-gray-200 border-dashed px-4 pt-2 pb-3 gap-3'>
      <div className='flex flex-col gap-1.5'>
        <div className='text-gray-900 text-[13px] font-medium'>
          Instructions:
        </div>
        <InstructionTooltip
          onCopy={() => onCopy(entry.majorVersion.properties.instructions)}
        >
          <div className='text-gray-900 text-[13px] font-normal px-3 py-2 bg-white rounded-[2px] border border-gray-200 whitespace-pre-wrap'>
            {entry.majorVersion.properties.instructions}
          </div>
        </InstructionTooltip>
      </div>
      <div className='flex flex-col gap-0.5'>
        <div className='text-gray-900 text-[13px] font-medium'>
          Temperature:
        </div>
        <div>
          <TaskTemperatureView
            temperature={entry.majorVersion.properties.temperature}
            className='text-gray-900 gap-0.5'
          />
        </div>
      </div>
    </div>
  );
}
