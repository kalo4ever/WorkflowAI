import { AlertDialog } from '../ui/AlertDialog';

type DeployVersionConfirmModalProps = {
  showConfirmModal: boolean;
  versionBadgeText: string | undefined;
  closeModal: () => void;
  onConfirm: () => Promise<void>;
};

export function DeployVersionConfirmModal(props: DeployVersionConfirmModalProps) {
  const { showConfirmModal, versionBadgeText, closeModal, onConfirm } = props;
  return (
    <AlertDialog
      open={showConfirmModal}
      title={'Confirm Deploy?'}
      subTitle={`Are you sure you want to deploy version ${versionBadgeText}?`}
      text={'Your environment will automatically begin using the updated AI agent version.'}
      confrimationText='Confirm Deploy'
      onCancel={closeModal}
      onConfirm={onConfirm}
    />
  );
}
