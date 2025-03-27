import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/Avatar/Avatar';
import { SimpleTooltip } from '@/components/ui/Tooltip';
import { User } from '@/types/user';

type UserAvatarProps = {
  tooltipText: string;
  user: Pick<User, 'firstName' | 'imageUrl'>;
};

export function UserAvatar(props: UserAvatarProps) {
  const { tooltipText, user } = props;

  return (
    <SimpleTooltip content={tooltipText}>
      <Avatar className='w-6 h-6 bg-purple-300'>
        <AvatarImage src={user.imageUrl ?? undefined} />
        <AvatarFallback className='bg-purple-100'>{`${user.firstName?.[0]?.toUpperCase() ?? ''}`}</AvatarFallback>
      </Avatar>
    </SimpleTooltip>
  );
}
