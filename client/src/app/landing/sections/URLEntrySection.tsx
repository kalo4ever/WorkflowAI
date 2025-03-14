import { SparkleFilled } from '@fluentui/react-icons';
import { cx } from 'class-variance-authority';
import { useCallback, useEffect, useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { NEW_TASK_MODAL_OPEN } from '@/lib/globalModal';
import { useQueryParamModal } from '@/lib/globalModal';
import {
  useParsedSearchParams,
  useRedirectWithParams,
} from '@/lib/queryString';
import { useSuggestedAgents } from '@/store/suggested_agents';
import { SuggestedAgentsSection } from './SuggestedAgentsSection/SuggestedAgentsSection';
import { isCompanyURL } from './untils';

const predefinedDescriptionsOrCompanyURLs = [
  'Extract Sentiment from a Review',
  'Amazon.com',
  'Generate Word Cloud from Customer Feedback',
  'Analyze Tone in User Comments',
  'Apple.com',
  'Identify Key Themes in Survey Responses',
  'Classify Emotions in Product Reviews',
  'Summarize Sentiment Analysis Results',
  'Visualize Sentiment Trends Over Time',
];

type PredefinedAgentSelectorsProps = {
  onDescriptionOrCompanyURLSelected: (descriptionOrCompanyURL: string) => void;
};

function PredefinedAgentSelectors(props: PredefinedAgentSelectorsProps) {
  const {
    onDescriptionOrCompanyURLSelected: onDescriptionOrCompanyURLSelected,
  } = props;

  return (
    <div className='flex flex-wrap gap-4 w-full max-w-[1024px] items-center justify-center'>
      {predefinedDescriptionsOrCompanyURLs.map((text) => (
        <div
          key={text}
          className='flex flex-row items-center justify-center gap-2 bg-gray-100 rounded-[2px] px-3 py-2 hover:bg-gray-200 cursor-pointer'
          onClick={() => onDescriptionOrCompanyURLSelected(text)}
        >
          <div className='text-[13px] font-semibold text-gray-800'>{text}</div>
        </div>
      ))}
    </div>
  );
}

type Props = {
  className?: string;
};

export function URLEntrySection(props: Props) {
  const { className } = props;
  const { companyURL, descriptionOrCompanyURL } = useParsedSearchParams(
    'companyURL',
    'descriptionOrCompanyURL'
  );

  const resetToInitialState = useSuggestedAgents(
    (state) => state.resetToInitialState
  );

  const redirectWithParams = useRedirectWithParams();

  const setCompanyURL = useCallback(
    (url: string) => {
      const lowerCaseURL = url.toLowerCase();

      resetToInitialState(lowerCaseURL);

      redirectWithParams({
        params: {
          companyURL: lowerCaseURL,
          descriptionOrCompanyURL: undefined,
        },
      });
    },
    [redirectWithParams, resetToInitialState]
  );

  const [entryField, setEntryField] = useState('');

  const [inProgress, setInProgress] = useState(false);

  const onPrefillCompanyURL = useCallback(
    (url: string) => {
      setInProgress(true);
      setEntryField(url);
      setCompanyURL(url);
      setTimeout(() => {
        setInProgress(false);
        setEntryField('');
      }, 1000);
    },
    [setCompanyURL]
  );

  const { openModal: openNewTaskModal } =
    useQueryParamModal(NEW_TASK_MODAL_OPEN);

  const onNewTask = useCallback(
    (description: string) => {
      openNewTaskModal({
        mode: 'new',
        redirectToPlaygrounds: 'true',
        prefilledDescription: description,
        descriptionOrCompanyURL: undefined,
      });
    },
    [openNewTaskModal]
  );

  const onDescriptionOrCompanyURLSelected = useCallback(
    (descriptionOrCompanyURL: string) => {
      if (isCompanyURL(descriptionOrCompanyURL)) {
        onPrefillCompanyURL(descriptionOrCompanyURL.toLowerCase());
      } else {
        setEntryField(descriptionOrCompanyURL);
        setInProgress(true);
        onNewTask(descriptionOrCompanyURL);
        setTimeout(() => {
          setInProgress(false);
          setEntryField('');
        }, 2000);
      }
    },
    [onPrefillCompanyURL, onNewTask]
  );

  useEffect(() => {
    if (!!descriptionOrCompanyURL) {
      onDescriptionOrCompanyURLSelected(descriptionOrCompanyURL);
    }
  }, [
    descriptionOrCompanyURL,
    onDescriptionOrCompanyURLSelected,
    redirectWithParams,
  ]);

  const isGenerateButtonActive = !inProgress && entryField.length > 0;

  if (!!companyURL) {
    return (
      <div
        className={cx(
          'flex flex-col items-center justify-center w-full h-max text-center px-4 pb-4',
          className
        )}
      >
        <SuggestedAgentsSection
          companyURL={companyURL}
          landingPageMode={true}
        />
      </div>
    );
  }

  return (
    <div
      className={cx(
        'flex flex-col items-center justify-center w-full text-center px-4 max-w-[1024px] flex-shrink-0 gap-6',
        className
      )}
    >
      <div
        className={cx(
          'flex w-full rounded-[4px] shadow-xl',
          inProgress ? 'bg-gray-100' : 'bg-custom-gradient-solid'
        )}
      >
        <div
          className={cx(
            'flex flex-row w-full items-center justify-between gap-2 m-1 px-2 py-2',
            inProgress ? 'bg-gray-100' : 'bg-white'
          )}
        >
          <Input
            placeholder='Enter your company URL or a description of what you want to build'
            className={cx(
              'w-full text-[16px] font-normal py-0 pr-0 pl-1 focus-visible:ring-0 border-none bg-transparent',
              inProgress ? 'text-gray-400' : 'text-gray-900'
            )}
            value={entryField}
            onChange={(event) => setEntryField(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && isGenerateButtonActive) {
                onDescriptionOrCompanyURLSelected(entryField);
              }
            }}
            autoFocus={true}
          />
          <Button
            variant='newDesignIndigo'
            icon={<SparkleFilled className='w-[20px] h-[20px]' />}
            size='none'
            className='px-3 py-2'
            disabled={!isGenerateButtonActive}
            onClick={() => onDescriptionOrCompanyURLSelected(entryField)}
            loading={inProgress}
          >
            {inProgress ? 'Thinking' : 'Generate'}
          </Button>
        </div>
      </div>
      <PredefinedAgentSelectors
        onDescriptionOrCompanyURLSelected={onDescriptionOrCompanyURLSelected}
      />
    </div>
  );
}
