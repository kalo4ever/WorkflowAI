import Link from 'next/link';
import { useCallback } from 'react';
import { displaySuccessToaster } from '@/components/ui/Sonner';
import { useIsAllowed } from '@/lib/hooks/useIsAllowed';
import { useVersions } from '@/store/versions';
import { TaskID, TaskSchemaID, TenantID } from '@/types/aliases';
import { VersionV1 } from '@/types/workflowAI';
import { taskVersionsRoute } from '../routeFormatter';
import { formatSemverVersion } from '../versionUtils';

type UseFavoriteToggleProps = {
  tenant: TenantID | undefined;
  taskId: TaskID;
};

export function useFavoriteToggle(props: UseFavoriteToggleProps) {
  const { tenant, taskId } = props;

  const { checkIfAllowed } = useIsAllowed();

  const favoriteVersion = useVersions((state) => state.favoriteVersion);
  const unfavoriteVersion = useVersions((state) => state.unfavoriteVersion);
  const handleFavoriteToggle = useCallback(
    async (version: VersionV1) => {
      if (!checkIfAllowed() || !tenant) {
        return;
      }
      const currentIsFavorite = version.is_favorite ?? false;
      const newIsFavorite = !currentIsFavorite;

      if (newIsFavorite) {
        await favoriteVersion(tenant, taskId, version.id);
      } else {
        await unfavoriteVersion(tenant, taskId, version.id);
      }

      const semverVersion = formatSemverVersion(version);

      displaySuccessToaster(
        <>
          <span>{`V${semverVersion} ${newIsFavorite ? 'Added to' : 'Removed from'} favorites. `}</span>
          <Link
            href={taskVersionsRoute(
              tenant,
              taskId,
              `${version.schema_id}` as TaskSchemaID,
              {
                filter: 'favorites',
              }
            )}
            className='underline cursor-pointer'
            onClick={(e) => e.stopPropagation()}
          >
            View Favorites
          </Link>
        </>
      );
    },
    [favoriteVersion, unfavoriteVersion, tenant, taskId, checkIfAllowed]
  );

  return { handleFavoriteToggle };
}
