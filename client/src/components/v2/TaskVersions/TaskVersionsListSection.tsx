import { FluentIcon } from '@fluentui/react-icons';
import { TaskVersionsContainer, TaskVersionsContainerProps } from '@/components/v2/TaskVersions/TaskVersionsContainer';
import { TaskVersionsListSectionHeader } from '@/components/v2/TaskVersions/TaskVersionsListSectionHeader';
import { VersionAvatarType } from '@/components/v2/TaskVersions/utils';
import { VersionV1 } from '@/types/workflowAI';

type TaskVersionsListSectionProps = TaskVersionsContainerProps & {
  allVersions: VersionV1[];
  icon?: FluentIcon;
  avatarType?: VersionAvatarType;
  title?: string;
};

export function TaskVersionsListSection(props: TaskVersionsListSectionProps) {
  const { icon, title, ...rest } = props;
  const finalTitle =
    title || (rest.avatarType === VersionAvatarType.Favorited ? `Favorites (${rest.allVersions.length})` : 'Deployed');
  if (rest.allVersions.length === 0) {
    return null;
  }
  return (
    <div className='flex flex-col'>
      <TaskVersionsListSectionHeader icon={icon} title={finalTitle} />
      <TaskVersionsContainer {...rest} className='p-4' />
    </div>
  );
}
