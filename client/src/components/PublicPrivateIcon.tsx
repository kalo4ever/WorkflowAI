import { LockClosedRegular, LockOpenRegular } from '@fluentui/react-icons';
import { cx } from 'class-variance-authority';

type PublicPrivateIconProps = {
  isPublic: boolean;
  className?: string;
};

export function PublicPrivateIcon(props: PublicPrivateIconProps) {
  const { isPublic, className } = props;
  const commonClassName = cx('h-4 w-4 text-gray-700 shrink-0', className);
  return isPublic ? (
    <LockOpenRegular className={commonClassName} />
  ) : (
    <LockClosedRegular className={commonClassName} />
  );
}
