import { Tag24Regular } from '@fluentui/react-icons';
import { useState } from 'react';
import { AIProviderIcon } from '@/components/icons/models/AIProviderIcon';
import { cn } from '@/lib/utils';
import { useOrFetchModels } from '@/store/fetchers';
import { ModelResponse } from '@/types/workflowAI';

type PriceSectionBarGraphProps = {
  percentage: number;
  price: number;
  color: string;
  providerName: string;
  subtitle: string;
};

function PriceSectionBarGraph(props: PriceSectionBarGraphProps) {
  const { percentage, price, color, providerName, subtitle } = props;

  return (
    <div className='flex sm:flex-row flex-col sm:gap-4 gap-1 w-full sm:items-center items-start'>
      <div className='sm:w-[112px] w-fit items-end text-right text-gray-500 text-[16px] font-medium'>
        {providerName}
      </div>
      <div className='flex flex-row gap-4 w-full h-full items-center'>
        <div className='flex flex-1 h-full'>
          <div className={cn('flex h-full', color)} style={{ width: `${percentage}%` }} />
        </div>
        <div className='w-[112px] flex flex-col justify-center sm:text-left text-right rounded-[2px]'>
          <div className='text-gray-700 text-[16px] font-medium'>${price}</div>
          <div className='text-gray-400 text-[12px] font-normal'>{subtitle}</div>
        </div>
      </div>
    </div>
  );
}

type PriceSectionGraphProps = {
  model: ModelResponse | undefined;
};

function PriceSectionGraph(props: PriceSectionGraphProps) {
  const { model } = props;

  if (!model) {
    return null;
  }

  const pricePerInputToken = model.metadata.price_per_input_token_usd * 1000000;

  const pricePerOutputToken = model.metadata.price_per_output_token_usd * 1000000;

  const maxPrice = Math.max(pricePerInputToken, pricePerOutputToken);

  return (
    <div className='flex flex-col w-full sm:gap-8 gap-4 bg-gray-100 rounded-[8px] sm:p-11 p-6'>
      <PriceSectionBarGraph
        percentage={90 * (pricePerInputToken / maxPrice)}
        price={pricePerInputToken}
        color='bg-indigo-200/60'
        providerName={model.metadata.provider_name}
        subtitle='/ 1M input tokens'
      />
      <PriceSectionBarGraph
        percentage={90 * (pricePerInputToken / maxPrice)}
        price={pricePerInputToken}
        color='bg-indigo-500'
        providerName='WorkflowAI'
        subtitle='/ 1M input tokens'
      />
      <PriceSectionBarGraph
        percentage={90 * (pricePerOutputToken / maxPrice)}
        price={pricePerOutputToken}
        color='bg-indigo-200/60'
        providerName={model.metadata.provider_name}
        subtitle='/ 1M output tokens'
      />
      <PriceSectionBarGraph
        percentage={90 * (pricePerOutputToken / maxPrice)}
        price={pricePerOutputToken}
        color='bg-indigo-500'
        providerName='WorkflowAI'
        subtitle='/ 1M output tokens'
      />
    </div>
  );
}

type PriceSectionModelSelectorItemProps = {
  model: ModelResponse;
  isSelected: boolean;
  onClick: () => void;
};

function PriceSectionModelSelectorItem(props: PriceSectionModelSelectorItemProps) {
  const { model, isSelected, onClick } = props;

  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center sm:w-[188px] h-full w-[115px] py-3 cursor-pointer border-b-2 shrink-0',
        isSelected
          ? 'text-gray-700 border-gray-700'
          : 'text-gray-500 border-gray-200 hover:border-gray-400 hover:text-gray-600'
      )}
      onClick={onClick}
    >
      <div className='flex flex-row gap-[6px] items-center justify-center'>
        <AIProviderIcon name={model.metadata.provider_name} sizeClassName='w-[14px] h-[14px]' />
        <div className='text-[16px] font-semibold'>{model.metadata.provider_name}</div>
      </div>
      <div className='text-[12px] font-normal text-center px-1'>{model.name}</div>
    </div>
  );
}

type PriceSectionModelSelectorProps = {
  models: ModelResponse[] | undefined;
  selectedModelIndex: number | undefined;
  setSelectedModelIndex: (modelIndex: number) => void;
};

function PriceSectionModelSelector(props: PriceSectionModelSelectorProps) {
  const { models, selectedModelIndex, setSelectedModelIndex } = props;

  return (
    <div className='flex flex-row items-center justify-center overflow-x-auto w-full scrollbar-hide'>
      {models?.map((model, index) => (
        <PriceSectionModelSelectorItem
          key={model.id}
          model={model}
          isSelected={selectedModelIndex === index}
          onClick={() => setSelectedModelIndex(index)}
        />
      ))}
    </div>
  );
}

type PriceSectionProps = {
  className?: string;
};

export function PriceSection(props: PriceSectionProps) {
  const { className } = props;

  const { models } = useOrFetchModels();
  const threeFirstModels = models?.slice(0, 3);
  const [selectedModelIndex, setSelectedModelIndex] = useState<number>(0);

  return (
    <div className={cn('flex flex-col gap-6 items-center sm:px-16 px-4 w-full max-w-[1260px]', className)}>
      <div className='flex flex-col gap-2 items-center justify-center'>
        <div className='flex flex-row gap-2 items-center justify-center'>
          <Tag24Regular className='text-gray-500' />
          <div className='text-gray-900 text-[30px] font-semibold'>Price Match</div>
        </div>
        <div className='text-gray-500 text-[18px] max-w-[630px] text-center font-normal'>
          Pay the same price per tokens than you would with OpenAI, Google, Anthropic. We make our margin on them, not
          you.
          <a
            className='underline ml-1 cursor-pointer'
            href='https://docs.workflowai.com/workflowai-cloud/pricing'
            target='_blank'
          >
            Learn more about our business model.
          </a>
        </div>
      </div>
      <PriceSectionModelSelector
        models={threeFirstModels}
        selectedModelIndex={selectedModelIndex}
        setSelectedModelIndex={setSelectedModelIndex}
      />
      <PriceSectionGraph model={threeFirstModels?.[selectedModelIndex]} />
    </div>
  );
}
