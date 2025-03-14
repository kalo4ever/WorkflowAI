import { Key16Regular, KeyMultiple16Regular } from '@fluentui/react-icons';
import { Button } from '@/components/ui/Button';
import { Checkbox } from '@/components/ui/Checkbox';
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from '@/components/ui/HoverCard';
import { APIKeyOption } from './ApiContent';

type APIKeySelectionProps = {
  selectedKeyOption: APIKeyOption | undefined;
  setSelectedKeyOption: (option: APIKeyOption | undefined) => void;
  provider: string | null | undefined;
  isOwnKeySupported: boolean;
  showApiKeyButton?: boolean;
  setShowApiKeyModal?: React.Dispatch<React.SetStateAction<boolean>>;
};

export function APIKeySelection(props: APIKeySelectionProps) {
  const {
    selectedKeyOption,
    setSelectedKeyOption,
    provider,
    isOwnKeySupported,
    showApiKeyButton = false,
    setShowApiKeyModal,
  } = props;

  const renderEditButton = () => {
    if (!showApiKeyButton) {
      return null;
    }
    if (selectedKeyOption !== APIKeyOption.Own) {
      return null;
    }
    return (
      <div>
        <Button
          variant='outline'
          onClick={() => setShowApiKeyModal?.(true)}
          className='text-slate-700'
        >
          Edit API Key
        </Button>
      </div>
    );
  };

  const renderHoverCardContent = () => {
    if (isOwnKeySupported) {
      return null;
    }

    return (
      <HoverCardContent
        className='px-[10px] py-[6px] bg-slate-700 text-white items-center justify-center rounded-[14px] w-fit'
        side='top'
      >
        <div>We don’t currently support user API keys for {provider}.</div>
        <div>If you would like to use your own keys please contact us.</div>
      </HoverCardContent>
    );
  };

  return (
    <div className='flex flex-col gap-2'>
      <div className='flex flex-row gap-4 rounded-[12px] border px-4 py-3 items-center'>
        <Checkbox
          checked={selectedKeyOption === APIKeyOption.WorkflowAI}
          onClick={() => setSelectedKeyOption(APIKeyOption.WorkflowAI)}
        />

        <div className='flex items-center justify-center bg-slate-100 w-10 h-10 rounded-full'>
          <KeyMultiple16Regular />
        </div>
        <div className='text-[14px] font-medium text-slate-700'>
          I’d like to use WorkflowAI’s keys (recommended).
        </div>
      </div>
      <div className='flex flex-row gap-4 rounded-[12px] border px-4 py-3 items-center'>
        <HoverCard>
          {renderHoverCardContent()}
          <HoverCardTrigger>
            <Checkbox
              checked={selectedKeyOption === APIKeyOption.Own}
              onClick={() => setSelectedKeyOption(APIKeyOption.Own)}
              disabled={!isOwnKeySupported}
            />
          </HoverCardTrigger>
        </HoverCard>
        <div className='flex items-center justify-center bg-slate-100 w-10 h-10 rounded-full'>
          <Key16Regular />
        </div>
        <div className='text-[14px] font-medium text-slate-700'>
          I’d like to use my own API key for {provider ?? '[provider]'}.
        </div>
      </div>
      <div className='text-slate-500 text-[12px] pt-2'>
        You will be charged the same price using WorkflowAI’s keys as your own.
      </div>
      {renderEditButton()}
    </div>
  );
}
