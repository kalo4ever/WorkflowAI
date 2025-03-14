import { AI_PROVIDERS_METADATA } from '@/components/AIModelsCombobox/utils';
import { cn } from '@/lib/utils/cn';
import { Provider } from '@/types/workflowAI';
import { MysteryModelIcon } from './mysteryModelIcon';

type AIProviderIconProps = {
  providerId: string | null | undefined;
  fallbackOnMysteryIcon?: boolean;
  sizeClassName?: string;
};

export function AIProviderIcon(props: AIProviderIconProps) {
  const {
    providerId,
    fallbackOnMysteryIcon,
    sizeClassName = 'w-5 h-5',
  } = props;

  const icon = AI_PROVIDERS_METADATA[providerId as Provider]?.icon;

  if (icon === undefined && !fallbackOnMysteryIcon) {
    return null;
  }

  return (
    <div className={cn('flex items-center justify-center', sizeClassName)}>
      {icon || <MysteryModelIcon />}
    </div>
  );
}

type AIProviderSVGIconProps = {
  providerId: string | null | undefined;
};

export function AIProviderSVGIcon(props: AIProviderSVGIconProps) {
  const { providerId } = props;

  const icon = AI_PROVIDERS_METADATA[providerId as Provider]?.icon;

  return icon;
}
