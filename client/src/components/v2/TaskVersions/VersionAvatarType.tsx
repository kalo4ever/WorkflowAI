import { capitalize } from 'lodash';
import { useMemo } from 'react';
import { UserAvatar } from '@/components/ui/Avatar/UserAvatar';
import { User } from '@/types/user';
import { VersionV1 } from '@/types/workflowAI';
import { VersionAvatarType } from './utils';

type TaskVersionAvatarProps = {
  avatarType: VersionAvatarType;
  usersByID: Record<string, User>;
  version: VersionV1;
};

export function TaskVersionAvatar(props: TaskVersionAvatarProps) {
  const { avatarType, version, usersByID } = props;

  const identifier = useMemo(() => {
    if (avatarType === VersionAvatarType.Deployed) {
      return version.deployments?.[0]?.deployed_by;
    }
    if (avatarType === VersionAvatarType.Favorited) {
      return version.favorited_by;
    }
    return version.created_by;
  }, [avatarType, version]);

  if (!identifier?.user_id) {
    return null;
  }

  const user = usersByID[identifier.user_id];

  if (!user) {
    return null;
  }

  return <UserAvatar tooltipText={`${capitalize(avatarType)} by ${user.firstName} ${user.lastName}`} user={user} />;
}
