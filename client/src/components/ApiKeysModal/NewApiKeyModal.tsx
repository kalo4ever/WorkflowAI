import { useCallback, useEffect, useState } from 'react';
import { APIKeyResponseCreated } from '@/types/workflowAI';
import { CopyContentButton } from '../buttons/CopyTextButton';
import { Button } from '../ui/Button';
import { Dialog, DialogContent } from '../ui/Dialog';
import { Input } from '../ui/Input';

type CreateKeyContentProps = {
  name: string;
  handleNameChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleSubmit: () => void;
  onClose: () => void;
};

function CreateKeyContent(props: CreateKeyContentProps) {
  const { name, handleNameChange, handleSubmit, onClose } = props;
  return (
    <>
      <div className='border-b border-dashed px-4 py-3 font-semibold text-gray-900'>
        Create New Secret Key
      </div>
      <div className='p-4 flex flex-col gap-2'>
        <div className='text-sm font-normal text-gray-700'>
          This API key is tied to your user and can make requests against the
          selected project. If you are removed from the organization or project,
          this key will be disabled.
        </div>
        <div className='text-xsm font-medium text-gray-700'>
          Name (Optional)
        </div>
        <Input
          placeholder='My Secret Key'
          value={name}
          onChange={handleNameChange}
        />
      </div>
      <div className='flex items-center justify-between px-4 py-3'>
        <Button variant='ghost' onClick={onClose}>
          Cancel
        </Button>
        <Button variant='newDesign' onClick={handleSubmit}>
          Create Secret Key
        </Button>
      </div>
    </>
  );
}

type SaveKeyContentProps = {
  newKey: string;
  onDone: () => void;
};

function SaveKeyContent(props: SaveKeyContentProps) {
  const { newKey, onDone } = props;

  return (
    <>
      <div className='border-b border-dashed px-4 py-3 font-semibold text-gray-900'>
        Save Your Key
      </div>
      <div className='p-4 flex flex-col gap-2'>
        <div className='text-xs font-normal text-gray-700 whitespace-pre-line'>
          <span>
            {`Please save this secret key somewhere safe and accessible. For
              security reasons, `}
          </span>
          <strong>you won&apos;t be able to view it again.</strong>
          <span>
            {` If you lose this
              API key, you'll need to generate a new one.`}
          </span>
        </div>
        <div className='text-xsm font-normal text-gray-900 px-3 py-2 border rounded-sm flex items-center gap-2 w-fit'>
          {newKey}
          <CopyContentButton text={newKey} />
        </div>
      </div>
      <div className='flex items-center justify-end px-4 py-3'>
        <Button variant='newDesign' onClick={onDone}>
          Done
        </Button>
      </div>
    </>
  );
}

type NewApiKeyModalProps = {
  open: boolean;
  onClose: () => void;
  onCreate: (name: string) => Promise<APIKeyResponseCreated | undefined>;
};

export function NewApiKeyModal(props: NewApiKeyModalProps) {
  const { open, onClose, onCreate } = props;
  const [name, setName] = useState('');
  const [newKey, setNewKey] = useState<string | undefined>();

  const handleNameChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setName(e.target.value);
    },
    []
  );

  const handleSubmit = useCallback(async () => {
    // If no name is provided, use the default name 'Secret Key'
    const finalName = name || 'Secret Key';
    const newApiKey = await onCreate(finalName);
    if (!newApiKey) {
      return;
    }
    setNewKey(newApiKey.key);
  }, [onCreate, name]);

  useEffect(() => {
    if (!open) {
      setName('');
      setNewKey(undefined);
    }
  }, [open]);

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className='p-0 gap-0 w-fit'>
        {newKey ? (
          <SaveKeyContent newKey={newKey} onDone={onClose} />
        ) : (
          <CreateKeyContent
            name={name}
            handleNameChange={handleNameChange}
            handleSubmit={handleSubmit}
            onClose={onClose}
          />
        )}
      </DialogContent>
    </Dialog>
  );
}
