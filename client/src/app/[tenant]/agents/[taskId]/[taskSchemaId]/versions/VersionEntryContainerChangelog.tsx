import { History16Regular } from '@fluentui/react-icons';
import { VersionEntry } from './utils';

type VersionEntryContainerChangelogProps = {
  entry: VersionEntry;
};

export function VersionEntryContainerChangelog(props: VersionEntryContainerChangelogProps) {
  const { entry } = props;
  const changelogs = entry.majorVersion?.previous_version?.changelog;

  if (!changelogs || changelogs.length === 0) {
    return null;
  }

  return (
    <div className='flex flex-col gap-2 bg-gray-100 rounded-[2px] px-3 py-2.5'>
      <div className='flex flex-row gap-2 items-center'>
        <History16Regular className='w-4 h-4 text-gray-500' />
        <div className='text-[13px] font-semibold text-gray-700'>Changelog</div>
      </div>
      <div className='flex flex-col gap-1.5'>
        {changelogs.map((changelog, index) => (
          <div key={`${index}`} className='flex flex-row gap-2 items-baseline pl-2'>
            <div className='w-[5px] h-[5px] rounded-full bg-gray-600 flex-shrink-0 relative -top-[2px]' />
            <div className='text-[13px] text-gray-600 whitespace-pre-line'>{changelog}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
