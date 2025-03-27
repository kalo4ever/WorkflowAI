'use client';

import { cx } from 'class-variance-authority';
import { useMemo } from 'react';
import { Button } from '@/components/ui/Button';

function TitleAndSteps(props: { title: string; step: number | undefined; numberOfSteps: number | undefined }) {
  const { title, step, numberOfSteps } = props;

  const textForSteps = useMemo(() => {
    if (step === undefined || numberOfSteps === undefined || (numberOfSteps === 1 && step === 1)) {
      return undefined;
    }

    return `Step ${step}/${numberOfSteps}`;
  }, [step, numberOfSteps]);

  if (textForSteps === undefined) {
    return <div className='text-[14px] font-medium text-slate-500'>{title}</div>;
  }

  return (
    <div className='flex flex-col gap-[2px]'>
      <div className='text-slate-500 text-[14px] font-light'>{textForSteps}</div>
      <div className='text-[18px] font-medium'>{title}</div>
    </div>
  );
}

type MultipleStepsGroupEntryProps = {
  title: string;
  titleForCompleted: string;
  continueTitle?: string;

  step?: number;
  numberOfSteps?: number;

  itemNames?: string[];
  itemSuffix?: string;
  itemsSuffix?: string;
  defaultNumberOfItemsForDisplay?: number;
  numberOfItemsToActivateContinue?: number;

  isInProgress: boolean;

  badgesClassName: string;
  floatingLook?: boolean;

  onClear?: () => void;
  onEdit?: () => void;
  onContinue?: () => Promise<void> | void;
  continueRoute?: string;

  children?: React.ReactNode;
};

export function MultipleStepsGroupEntry(props: MultipleStepsGroupEntryProps) {
  const {
    title,
    titleForCompleted,
    continueTitle,

    step,
    numberOfSteps,

    itemNames = [],
    itemSuffix,
    itemsSuffix,
    defaultNumberOfItemsForDisplay,
    numberOfItemsToActivateContinue = 1,

    isInProgress,

    badgesClassName,
    floatingLook = true,

    onClear,
    onEdit,
    onContinue,
    continueRoute,

    children,
  } = props;

  const isCompleted = itemNames.length >= numberOfItemsToActivateContinue;

  const numberOfIterationText = useMemo(() => {
    if (itemsSuffix === undefined || itemSuffix === undefined) {
      return undefined;
    }

    let numberOfItems = itemNames.length;
    if (numberOfItems === 0 && !!defaultNumberOfItemsForDisplay) {
      numberOfItems = defaultNumberOfItemsForDisplay;
    }

    if (numberOfItems === 0) {
      return `No ${itemSuffix} selected`;
    } else if (numberOfItems === 1) {
      return `1 ${itemSuffix} selected`;
    } else {
      return `${numberOfItems} ${itemsSuffix} selected`;
    }
  }, [itemNames, itemSuffix, itemsSuffix, defaultNumberOfItemsForDisplay]);

  return (
    <div className={cx('flex flex-col w-full', floatingLook && 'bg-white rounded-[16px] shadow-modal')}>
      <div
        className={cx(
          'flex flex-row w-full justify-between items-center overflow-hidden',
          floatingLook ? 'px-4 pt-2.5' : 'pr-4',
          isInProgress && floatingLook && 'border-b',
          !isInProgress && !isCompleted && 'opacity-35',
          (isInProgress || !isCompleted) && 'pb-2.5'
        )}
      >
        {isCompleted && !isInProgress ? (
          <div className='flex flex-col w-max mr-[16px] overflow-hidden'>
            <div className='text-[18px] font-medium'>{titleForCompleted}</div>
            <div className='w-full overflow-hidden flex pb-3'>
              <div className='flex-1 flex gap-[4px] w-full text-slate-700 overflow-y-auto'>
                {itemNames.map((text) => (
                  <div
                    key={text}
                    className={cx(
                      badgesClassName,
                      'truncate px-[8px] py-[4px] rounded-[8px] text-[12px] items-center whitespace-nowrap'
                    )}
                    title={text}
                  >
                    {text}
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <TitleAndSteps title={title} step={step} numberOfSteps={numberOfSteps} />
        )}

        {isCompleted && !isInProgress && (
          <Button variant='outline' onClick={onEdit} className='text-slate-700 mb-2.5'>
            Edit
          </Button>
        )}

        {isInProgress && (
          <div className='flex flex-row items-center'>
            {!!numberOfIterationText && (
              <div className='border-r pr-[8px] font-normal text-slate-500 text-[14px]'>{numberOfIterationText}</div>
            )}
            {!!onClear && (
              <Button variant='text' disabled={!isCompleted} onClick={onClear} className='pl-[8px] pr-[16px]'>
                Clear Selection
              </Button>
            )}
            {!!continueTitle && (
              <Button disabled={!isCompleted} onClick={onContinue} toRoute={continueRoute}>
                {continueTitle}
              </Button>
            )}
          </div>
        )}
      </div>
      {isInProgress && <div className={cx(floatingLook ? 'py-4 px-4' : 'pr-4')}>{children}</div>}
    </div>
  );
}
