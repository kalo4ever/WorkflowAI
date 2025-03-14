import { Dismiss12Filled } from '@fluentui/react-icons';
import { cx } from 'class-variance-authority';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { SearchFieldParam } from '@/lib/routeFormatter';
import { SearchFields } from '@/types/workflowAI';
import { TaskRunSearchFieldHints } from './TaskRunSearchFieldHints';
import { findHints } from './TaskRunSearchFieldUtils';

const HINT_CLASSNAMES = {
  [SearchFieldParam.FieldNames]: 'text-gray-900 px-1.5',
  [SearchFieldParam.Operators]: 'text-gray-500 px-1.5',
  [SearchFieldParam.Values]: 'text-gray-900 px-1.5',
};

type TaskRunSearchFieldParametersBadgesProps = {
  index: number;
  parameters: [SearchFieldParam, string][];
  searchFields: SearchFields | undefined;
  setParam: (key: string, text: string | undefined, index: number) => void;
  onClear: (index: number) => void;
};

export function TaskRunSearchFieldParametersBadges(
  props: TaskRunSearchFieldParametersBadgesProps
) {
  const { index, parameters, searchFields, setParam, onClear } = props;

  const fieldName = useMemo(() => {
    return parameters.find(([key]) => key === SearchFieldParam.FieldNames)?.[1];
  }, [parameters]);

  const [keyForPopoverToShow, setKeyForPopoverToShow] = useState<
    string | undefined
  >(undefined);

  const handleClosePopover = useCallback(() => {
    setKeyForPopoverToShow(undefined);
  }, []);

  const selectKeyForPopoverToShow = useCallback((key: string) => {
    setKeyForPopoverToShow(key);
  }, []);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (
        event.key === 'Backspace' &&
        keyForPopoverToShow &&
        keyForPopoverToShow !== SearchFieldParam.Operators
      ) {
        setParam(keyForPopoverToShow, undefined, index);
        setKeyForPopoverToShow(undefined);
        return;
      }

      if (
        event.key === 'Enter' &&
        keyForPopoverToShow === SearchFieldParam.Values
      ) {
        setParam(keyForPopoverToShow, undefined, index);
        setKeyForPopoverToShow(undefined);
        return;
      }

      if (keyForPopoverToShow === SearchFieldParam.Values) {
        setParam(keyForPopoverToShow, undefined, index);
        setKeyForPopoverToShow(undefined);
        return;
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [keyForPopoverToShow, setParam, index]);

  const hintsDictionary: Record<string, string[]> = useMemo(() => {
    const parameters = [
      SearchFieldParam.FieldNames,
      SearchFieldParam.Operators,
      SearchFieldParam.Values,
    ];
    const result: Record<string, string[]> = {};
    parameters.forEach((param) => {
      result[param] = findHints(param, fieldName, searchFields) ?? [];
    });
    return result;
  }, [searchFields, fieldName]);

  const allParametersWereEntered = parameters.length === 3;

  return (
    <div
      className={cx(
        'flex flex-row w-max text-gray-900 font-medium text-[13px] h-6 items-center border-gray-200',
        parameters.length === 0 && 'hidden',
        allParametersWereEntered
          ? 'border rounded-[2px] mr-1'
          : 'border-l border-t border-b rounded-l-[2px] pr-1'
      )}
    >
      {parameters.map(([key, value]) => (
        <div key={key} className='h-full'>
          <div
            className={cx(
              'flex w-max h-full cursor-pointer items-center border-gray-200 border-r',
              HINT_CLASSNAMES[key],
              keyForPopoverToShow === key ? 'bg-gray-200' : 'hover:bg-gray-100'
            )}
            onClick={() => selectKeyForPopoverToShow(key)}
          >
            {value}
          </div>
          <TaskRunSearchFieldHints
            currentValue={value}
            options={hintsDictionary[key]}
            isVisible={keyForPopoverToShow === key}
            onSelect={(text) => setParam(key, text, index)}
            onClose={handleClosePopover}
            labelClassName={HINT_CLASSNAMES[key]}
          />
        </div>
      ))}
      {!!allParametersWereEntered && (
        <div
          className='flex items-center justify-center w-[22px] h-full min-h-6 cursor-pointer hover:bg-gray-100'
          onClick={() => onClear(index)}
        >
          <Dismiss12Filled className='w-3 h-3 text-gray-700' />
        </div>
      )}
    </div>
  );
}
