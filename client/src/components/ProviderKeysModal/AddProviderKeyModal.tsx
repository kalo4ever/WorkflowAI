'use client';

import {
  Dispatch,
  SetStateAction,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { Button } from '@/components/ui/Button';
import { Dialog, DialogContent } from '@/components/ui/Dialog';
import { Input } from '@/components/ui/Input';
import {
  displayErrorToaster,
  displaySuccessToaster,
} from '@/components/ui/Sonner';
import { RequestError } from '@/lib/api/client';
import { ProviderConfig } from '@/store/organization_settings';
import { Provider, ProviderSettings } from '@/types/workflowAI';
import { OrganizationSettings } from '@/types/workflowAI';
import { AI_PROVIDERS_METADATA } from '../AIModelsCombobox/utils';

type SetProviderConfigProps = {
  providerSettings: ProviderSettings[] | undefined;
  currentProvider: string | undefined | null;
  onSetProviderConfig(
    provider: Provider,
    value: Record<string, unknown>
  ): Promise<void>;
  onClose: (keyWasCreated: boolean) => void;
};

type GoogleConfigFormProps = {
  setConfig: Dispatch<SetStateAction<Record<string, unknown> | undefined>>;
};

function GoogleConfigForm(props: GoogleConfigFormProps) {
  const { setConfig } = props;

  const [projectId, setProjectId] = useState<string>();
  const [location, setLocation] = useState<string>();
  const [credentials, setCredentials] = useState<string>();

  const onProjectIdChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setProjectId(e.target.value);
    },
    []
  );

  const onLocationChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setLocation(e.target.value);
    },
    []
  );

  const onCredentialsChange = useCallback(
    async (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = () => {
        const data = reader.result as string;
        setCredentials(data);
      };
      reader.readAsDataURL(file);
    },
    []
  );

  useEffect(() => {
    if (!projectId || !location || !credentials) {
      setConfig(undefined);
      return;
    }

    setConfig({
      vertex_project: projectId,
      vertex_location: location,
      vertex_credentials: credentials,
    });
  }, [projectId, location, credentials, setConfig]);

  return (
    <div className='flex flex-col items-start gap-6 w-full'>
      <div className='flex flex-col items-start gap-3 w-full max-w-[600px]'>
        <label
          htmlFor='project-id'
          className='text-[14px] text-slate-600 font-medium'
        >
          Project ID
        </label>
        <Input
          id='project-id'
          placeholder='The ID of your Google Vertex Project'
          onChange={onProjectIdChange}
          value={projectId}
          className='w-full rounded-[10px]'
        />
      </div>

      <div className='flex flex-col items-start gap-3 w-full max-w-[600px]'>
        <label
          htmlFor='location'
          className='text-[14px] text-slate-600 font-medium'
        >
          Location
        </label>
        <Input
          id='location'
          placeholder='The region of the project, eg. us-central1'
          onChange={onLocationChange}
          value={location}
          className='w-full rounded-[10px]'
        />
      </div>

      <div className='flex flex-col items-start gap-3 w-full max-w-[600px]'>
        <label
          htmlFor='credentials'
          className='text-[14px] text-slate-600 font-medium'
        >
          Credentials
        </label>
        <Input
          type='file'
          id='Credentials'
          placeholder='JSON file containing sign-in info'
          onChange={onCredentialsChange}
          className='w-full rounded-[10px]'
        />
      </div>
    </div>
  );
}

type ProviderConfigFormProps = {
  current_provider: Provider;
  setConfig: Dispatch<SetStateAction<Record<string, unknown> | undefined>>;
};

function ProviderConfigForm(props: ProviderConfigFormProps) {
  const { current_provider, setConfig } = props;

  const [apiKey, setApiKey] = useState<string>();

  useEffect(() => {
    if (!apiKey) {
      setConfig(undefined);
      return;
    }

    setConfig({ api_key: apiKey });
  }, [apiKey, setConfig]);

  const onChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setApiKey(e.target.value);
  }, []);

  const placeholder: string = useMemo(() => {
    switch (current_provider) {
      case 'anthropic':
        return 'Your Anthropic API Key';
      case 'azure_openai':
        return 'Your Azure OpenAI API Key';
      case 'google':
        return 'Your Google Vertex Credentials';
      case 'amazon_bedrock':
        return 'Your Amazon Bedrock Credentials';
      case 'groq':
        return 'Your Groq API Key';
      case 'openai':
        return 'Your OpenAI API Key';
      case 'mistral_ai':
        return 'Your Mistral AI API Key';
      case 'google_gemini':
        return 'Your Gemini API Key';
      case 'fireworks':
        return 'Your Fireworks API Key';
    }
  }, [current_provider]);

  return (
    <div className='flex flex-col items-start gap-3 w-full max-w-[600px]'>
      <label
        htmlFor='api-key'
        className='text-[14px] text-slate-600 font-medium'
      >
        API Key
      </label>
      <Input
        id='api-key'
        placeholder={placeholder}
        onChange={onChange}
        value={apiKey}
        className='w-full rounded-[10px] mb-32'
      />
    </div>
  );
}

export function AddProviderKeyModalContent(props: SetProviderConfigProps) {
  const { currentProvider, onSetProviderConfig, onClose } = props;

  const providerMetadata = AI_PROVIDERS_METADATA[currentProvider as Provider];

  const [config, setConfig] = useState<Record<string, unknown>>();

  const onAddConfigClick = useCallback(() => {
    if (!config) {
      return;
    }

    return onSetProviderConfig(currentProvider as Provider, config);
  }, [currentProvider, onSetProviderConfig, config]);

  const handleCancel = useCallback(() => {
    onClose(false);
  }, [onClose]);

  if (!providerMetadata) {
    return null;
  }

  return (
    <>
      <div className='flex flex-col items-start px-6 py-5 gap-6'>
        <div className='flex flex-row justify-between items-center w-full'>
          <div className='font-medium text-[20px] text-slate-900'>
            Add Model Provider Keys
          </div>
        </div>
        <div className='flex flex-row items-center gap-4 pt-3'>
          <div className='w-10 h-10 flex items-center justify-center bg-slate-50 rounded-[8px]'>
            {providerMetadata.icon}
          </div>
          <div className='text-slate-700 text-[14px] font-medium'>
            {providerMetadata.name ?? currentProvider}
          </div>
        </div>
        {providerMetadata.documentationUrl && (
          <div className='text-[14px] text-normal text-slate-600'>
            Get your{' '}
            <a
              href={providerMetadata.documentationUrl}
              className='text-blue-600 underline font-semibold'
              target='_blank'
            >
              Provider API Key
            </a>{' '}
            and enter it here.
          </div>
        )}
        {currentProvider === 'google' ? (
          <GoogleConfigForm setConfig={setConfig} />
        ) : (
          <ProviderConfigForm
            current_provider={currentProvider as Provider}
            setConfig={setConfig}
          />
        )}
      </div>
      <div className='flex gap-[8px] w-full justify-between px-[24px] py-[12px] bg-slate-50 border-t'>
        <Button variant='link' onClick={handleCancel}>
          <div>Cancel</div>
        </Button>
        <Button variant='default' disabled={!config} onClick={onAddConfigClick}>
          Add Key
        </Button>
      </div>
    </>
  );
}

type AddProviderKeyModalProps = {
  currentProvider: string | null | undefined;
  organizationSettings: OrganizationSettings | undefined;
  open: boolean;
  onClose: (keyWasCreated: boolean) => void;
  addProviderConfig: (provider: ProviderConfig) => Promise<void>;
};

export function AddProviderKeyModal(props: AddProviderKeyModalProps) {
  const {
    currentProvider,
    organizationSettings,
    open,
    onClose,
    addProviderConfig,
  } = props;

  const onSetProviderConfig = useCallback(
    async (provider: Provider, value: Record<string, unknown>) => {
      try {
        await addProviderConfig({
          provider,
          ...value,
        });
        displaySuccessToaster('Provider Key Added');
        onClose(true);
      } catch (e: unknown) {
        if (e instanceof RequestError) {
          displayErrorToaster('Invalid Provider Key');
          return;
        }
        throw e;
      }
    },
    [addProviderConfig, onClose]
  );

  const onOpenChange = useCallback(
    (open: boolean) => {
      if (!open) {
        onClose(false);
      }
    },
    [onClose]
  );

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className='w-[440px] max-w-[90vw] p-0 overflow-hidden'>
        <AddProviderKeyModalContent
          providerSettings={organizationSettings?.providers}
          currentProvider={currentProvider}
          onSetProviderConfig={onSetProviderConfig}
          onClose={onClose}
        />
      </DialogContent>
    </Dialog>
  );
}
