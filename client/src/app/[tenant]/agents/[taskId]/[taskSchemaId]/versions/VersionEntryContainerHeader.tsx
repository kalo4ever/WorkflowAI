import dayjs from 'dayjs';
import { useMemo } from 'react';
import { UserAvatar } from '@/components/ui/Avatar/UserAvatar';
import { useOrFetchClerkUsers } from '@/store/fetchers';
import { VersionEntry } from './utils';

type VersionEntryContainerHeaderProps = {
  entry: VersionEntry;
  previousEntry: VersionEntry | undefined;
  isLatest: boolean;
};

export function VersionEntryContainerHeader(
  props: VersionEntryContainerHeaderProps
) {
  const { entry, previousEntry, isLatest } = props;

  const adaptedFromMajor = entry.majorVersion.previous_version?.major;
  const relativeTime = dayjs(entry.majorVersion.created_at).fromNow();

  const userId = entry.majorVersion.created_by?.user_id;
  const userIds = userId ? [userId] : [];

  const { usersByID } = useOrFetchClerkUsers(userIds);

  const user = useMemo(() => {
    if (!userId) {
      return undefined;
    }
    return usersByID[userId];
  }, [usersByID, userId]);

  const showAdaptedFromVersion = useMemo(() => {
    if (!adaptedFromMajor) {
      return false;
    }

    if (entry.majorVersion.major - 1 === adaptedFromMajor) {
      return false;
    }

    if (entry.majorVersion.major === adaptedFromMajor) {
      return false;
    }

    if (
      !!previousEntry &&
      adaptedFromMajor === previousEntry.majorVersion.major
    ) {
      return false;
    }

    return true;
  }, [adaptedFromMajor, entry.majorVersion.major, previousEntry]);

  return (
    <div className='flex flex-row justify-between items-center h-[52px] px-4 bg-white border-b border-gray-200 border-dashed'>
      <div className='flex flex-row items-center gap-1.5'>
        <div className='text-[13px] font-medium text-gray-700 px-1.5 py-0.5 rounded-[2px] border-gray-200 border'>
          Version {entry.majorVersion.major}
        </div>
        {showAdaptedFromVersion && (
          <div className='text-[13px] font-medium text-gray-700 px-1.5 py-0.5 rounded-[2px] bg-gray-200'>
            Adapted from Version {adaptedFromMajor}
          </div>
        )}
        {isLatest && (
          <div className='text-[13px] font-medium text-gray-50 px-1.5 py-0.5 rounded-[2px] bg-gray-700'>
            Latest
          </div>
        )}
      </div>

      <div className='flex flex-row items-center gap-2'>
        {user && (
          <UserAvatar
            tooltipText={`Created by ${user.firstName} ${user.lastName}`}
            user={user}
          />
        )}
        <div className='text-[13px] font-base text-gray-500'>
          {relativeTime}
        </div>
      </div>
    </div>
  );
}
