import { ArrowUpFilled } from '@fluentui/react-icons';
import { cx } from 'class-variance-authority';
import { useCallback, useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Textarea } from '../ui/Textarea';

type NewTaskSuggestedFeaturesHeaderProps = {
  userMessage: string;
  setUserMessage: (message: string) => void;
  onSendIteration: () => Promise<void>;
  loading: boolean;
};

export function NewTaskSuggestedFeaturesHeader(props: NewTaskSuggestedFeaturesHeaderProps) {
  const { userMessage, setUserMessage, onSendIteration, loading } = props;
  const [inProgress, setInProgress] = useState(false);
  const isLoading = loading || inProgress;

  const onSendMessage = useCallback(async () => {
    setInProgress(true);

    await onSendIteration();

    setTimeout(() => {
      setInProgress(false);
    }, 1000);
  }, [onSendIteration]);

  const isGenerateButtonActive = !isLoading && userMessage.length > 0;

  const [isFocused, setIsFocused] = useState(false);
  const showGradientBorder = !isLoading && isFocused;

  const showSendButton = userMessage.length > 0 || isFocused;

  return (
    <div className='flex flex-col gap-2 w-full'>
      <div
        className={cx(
          'flex w-full rounded-[4px]',
          showGradientBorder ? 'bg-custom-gradient-solid shadow-md' : 'bg-gray-200'
        )}
      >
        <div
          className={cx(
            'flex flex-row w-full items-center justify-between gap-2 rounded-[2px]',
            isLoading ? 'bg-gray-100' : 'bg-white',
            showGradientBorder ? 'm-[2px] px-2 py-1' : 'm-[1px] px-[9px] py-[5px]'
          )}
        >
          <Textarea
            value={userMessage}
            onChange={(event) => setUserMessage(event.target.value)}
            placeholder='Write a description of the feature you want to build.'
            className={cx(
              'w-full text-[16px] font-normal pt-2 pb-[6px] pr-0 pl-1 focus-visible:ring-0 border-none bg-transparent max-h-[300px] scrollbar-hide',
              isLoading ? 'text-gray-400' : 'text-gray-900'
            )}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && isGenerateButtonActive) {
                event.preventDefault();
                onSendMessage();
              }
            }}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            autoFocus={true}
          />
          {showSendButton && (
            <Button
              variant='newDesignIndigo'
              icon={<ArrowUpFilled className='w-3.5 h-3.5' />}
              size='none'
              className={cx(
                'w-8 h-8 rounded-full flex-shrink-0 disabled:text-gray-400 disabled:opacity-100',
                isGenerateButtonActive
                  ? 'bg-custom-indigo-gradient'
                  : isLoading
                    ? 'bg-gray-50 disabled:bg-gray-50'
                    : 'bg-gray-100 disabled:bg-gray-100'
              )}
              disabled={!isGenerateButtonActive}
              onClick={() => onSendMessage()}
              loading={isLoading}
            />
          )}
        </div>
      </div>
    </div>
  );
}
