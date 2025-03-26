import { cx } from 'class-variance-authority';
import React from 'react';
import { SimpleTooltip } from '@/components/ui/Tooltip';

type RootObjectListSwitchProps = {
  onToggle: () => void;
  isRootObject: boolean;
};

export function RootObjectListSwitch(props: RootObjectListSwitchProps) {
  const { onToggle, isRootObject } = props;

  const commonClassNames =
    'flex items-center justify-center h-full rounded-[2px] px-2.5 py-1.5 text-sm font-normal transition-colors';
  const enabledClassNames = 'cursor-pointer hover:bg-gray-200 bg-transparent! text-gray-500';
  const disabledClassNames = 'bg-white text-gray-800 border-gray-300 border shadow-sm';

  return (
    <div className='h-9 w-fit flex items-center bg-gray-100 rounded-[2px] border border-gray-300 p-1 gap-1 ml-2 font-lato'>
      <SimpleTooltip content='Pick one if you only want one item' align='start'>
        <div
          className={cx(commonClassNames, !isRootObject ? enabledClassNames : disabledClassNames)}
          onClick={isRootObject ? undefined : onToggle}
        >
          Single
        </div>
      </SimpleTooltip>
      <SimpleTooltip content='Pick if you want multiple instances of entries' align='start'>
        <div
          className={cx(commonClassNames, isRootObject ? enabledClassNames : disabledClassNames)}
          onClick={isRootObject ? onToggle : undefined}
        >
          List
        </div>
      </SimpleTooltip>
    </div>
  );
}
