import { useCallback } from 'react';
import { Button } from '@/components/ui/Button';
import { APIKeyResponse } from '@/types/workflowAI';

type ManageApiKeysButtonProps = {
  apiKeys: APIKeyResponse[];
  openApiKeysModal: () => void;
  disabled: boolean;
};

export function ManageApiKeysButton(props: ManageApiKeysButtonProps) {
  const { apiKeys, openApiKeysModal, disabled } = props;
  const hasApiKeys = apiKeys.length > 0;

  const handleClick = useCallback(() => {
    openApiKeysModal();
  }, [openApiKeysModal]);

  return (
    <div>
      <Button variant={hasApiKeys ? 'newDesign' : 'newDesignIndigo'} onClick={handleClick} disabled={disabled}>
        {hasApiKeys ? 'Manage Secret Keys' : 'Create Secret Key'}
      </Button>
    </div>
  );
}
