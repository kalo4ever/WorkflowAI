import {
  CheckmarkCircle16Filled,
  Question16Regular,
} from '@fluentui/react-icons';
import { Sparkle16Filled } from '@fluentui/react-icons';
import { cx } from 'class-variance-authority';
import { SimpleTooltip } from '@/components/ui/Tooltip';

function getStateClassName(state: 'positive' | 'negative' | 'unsure'): string {
  switch (state) {
    case 'positive':
      return 'bg-green-200 hover:bg-green-400 text-green-700';
    case 'negative':
      return 'bg-red-200 hover:bg-red-400 text-red-700';
    case 'unsure':
      return 'hover:bg-gray-300 border border-gray-400 border-dashed text-gray-600';
  }
}

function getUserStateClassName(
  state: 'positive' | 'negative' | 'unsure'
): string {
  switch (state) {
    case 'positive':
      return 'bg-green-200 text-green-600';
    case 'negative':
      return 'bg-red-200 text-red-600';
    default:
      return '';
  }
}

function getAIStateClassName(
  state: 'positive' | 'negative' | 'unsure'
): string {
  switch (state) {
    case 'positive':
      return 'text-green-600 border border-green-500 border-dashed';
    case 'negative':
      return 'text-red-600 border border-red-400 border-dashed';
    default:
      return '';
  }
}

type BenchmarkReviewsEntryProps = {
  count: number;
  state: 'positive' | 'negative' | 'unsure';
  onClick: () => void;
  userCount?: number;
  aiCount?: number;
  alwaysShowCount?: boolean;
};

export function BenchmarkReviewsEntry(props: BenchmarkReviewsEntryProps) {
  const {
    count,
    state,
    onClick,
    userCount = 0,
    aiCount = 0,
    alwaysShowCount = false,
  } = props;

  if (count === 0 && !alwaysShowCount) {
    return null;
  }

  const className = getStateClassName(state);
  const userClassName = getUserStateClassName(state);
  const aiClassName = getAIStateClassName(state);

  const showQuestionMark = state === 'unsure';

  return (
    <SimpleTooltip
      asChild
      tooltipClassName='bg-white border border-gray-300 rounded-[2px] shadow-[0px_1px_3px_rgba(0,0,0,0.3)] px-2.5 py-2'
      side='top'
      align='center'
      tooltipDelay={100}
      content={
        <div
          className='flex flex-col font-lato text-[12px] text-gray-600 font-normal items-center justify-center cursor-pointer'
          onClick={onClick}
        >
          <div>Tap to view reviewed runs</div>
          {userCount + aiCount > 0 && (
            <div className='flex flex-row gap-1.5 pt-2'>
              {userCount > 0 && (
                <div
                  className={cx(
                    'flex items-center justify-center w-7 h-7 rounded-[2px] text-xs font-semibold cursor-pointer relative',
                    userClassName
                  )}
                >
                  {userCount}
                  <div className='w-[17px] h-[17px] absolute -top-[6px] -right-[6px] flex items-center justify-center'>
                    <CheckmarkCircle16Filled className='w-4 h-4' />
                  </div>
                </div>
              )}
              {aiCount > 0 && (
                <div
                  className={cx(
                    'flex items-center justify-center w-7 h-7 rounded-[2px] text-xs font-semibold cursor-pointer relative',
                    aiClassName
                  )}
                >
                  {aiCount}
                  <div className='w-[17px] h-[17px] absolute -top-[6px] -right-[6px] flex items-center justify-center rounded-full bg-white'>
                    <Sparkle16Filled className='w-4 h-4' />
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      }
    >
      <div
        className={cx(
          'flex items-center justify-center w-7 h-7 rounded-[2px] text-xs font-semibold cursor-pointer relative',
          className
        )}
        onClick={onClick}
      >
        {count}
        {showQuestionMark && (
          <div className='w-[17px] h-[17px] absolute -top-[6px] -right-[7px] flex items-center justify-center rounded-full bg-white'>
            <Question16Regular className='w-4 h-4 text-gray-400' />
          </div>
        )}
      </div>
    </SimpleTooltip>
  );
}
