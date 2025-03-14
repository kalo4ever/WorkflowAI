import { DismissFilled, SearchRegular } from '@fluentui/react-icons';
import { cx } from 'class-variance-authority';
import { useCallback, useMemo, useRef, useState } from 'react';
import {
  useParsedSearchParams,
  useRedirectWithParams,
} from '@/lib/queryString';
import { SearchFieldParam } from '@/lib/routeFormatter';
import { SearchFields } from '@/types/workflowAI';
import { TaskRunSearchFieldHints } from './TaskRunSearchFieldHints';
import { TaskRunSearchFieldInput } from './TaskRunSearchFieldInput';
import { TaskRunSearchFieldParametersBadges } from './TaskRunSearchFieldParametersBadges';
import {
  add,
  areAllFieldsSetInParams,
  exchange,
  findActiveIndex,
  findAndFilterHints,
  findCurrentIndex,
  findCurrentParamToEnter,
  findHints,
  findLastDefinedKey,
  findLastFieldName,
  findParametersForBadges,
  remove,
} from './TaskRunSearchFieldUtils';

type TaskRunSearchFieldProps = {
  className?: string;
  searchFields: SearchFields | undefined;
  defaultOperatorsForFields: Record<string, string>;
};

const parameters = [
  SearchFieldParam.FieldNames,
  SearchFieldParam.Operators,
  SearchFieldParam.Values,
];

export function TaskRunSearchField(props: TaskRunSearchFieldProps) {
  const { className, searchFields, defaultOperatorsForFields } = props;

  const currentQueryParams = useParsedSearchParams(...parameters);
  const [localQueryParams, setLocalQueryParams] = useState<
    Record<string, string | undefined>
  >({});

  const allCurrentAndLocalQueryParams: Record<string, string | undefined> =
    useMemo(() => {
      return { ...currentQueryParams, ...localQueryParams };
    }, [currentQueryParams, localQueryParams]);

  const fieldNames = useMemo(
    () =>
      allCurrentAndLocalQueryParams[SearchFieldParam.FieldNames]?.split(','),
    [allCurrentAndLocalQueryParams]
  );
  const operators = useMemo(
    () => allCurrentAndLocalQueryParams[SearchFieldParam.Operators]?.split(','),
    [allCurrentAndLocalQueryParams]
  );
  const values = useMemo(
    () => allCurrentAndLocalQueryParams[SearchFieldParam.Values]?.split(','),
    [allCurrentAndLocalQueryParams]
  );

  const numberOfParametersEntered: number =
    (fieldNames?.length ?? 0) +
    (operators?.length ?? 0) +
    (values?.length ?? 0);

  const currentParamToEnter: SearchFieldParam = useMemo(
    () => findCurrentParamToEnter(fieldNames, operators, values),
    [fieldNames, operators, values]
  );

  const [text, setText] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const redirectWithParams = useRedirectWithParams();

  const activeIndex = useMemo(
    () => findActiveIndex(fieldNames, operators, values),
    [fieldNames, operators, values]
  );

  const currentIndex = useMemo(
    () => findCurrentIndex(fieldNames, operators, values),
    [fieldNames, operators, values]
  );

  const [isFocused, setIsFocused] = useState(false);
  const blurTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const setParam = useCallback(
    (key: string, text: string | undefined, index: number) => {
      setText('');

      let newParams = { ...allCurrentAndLocalQueryParams };

      if (key === SearchFieldParam.FieldNames && !!text) {
        // Special case for field names, we need to remove the previous field name and move it to the end
        newParams = remove(index, newParams);
        newParams = add(
          newParams,
          text,
          text ? defaultOperatorsForFields[text] : undefined,
          undefined
        );
      } else if (key === SearchFieldParam.FieldNames && !text) {
        // Special case for field names, if we remove the field name, we remove the whole entry
        newParams = remove(index, newParams);
      } else if (key === SearchFieldParam.Values && !text) {
        // Special case for values, we need to remove the previous value and move the previous field name and operator to the end
        const fieldName = fieldNames?.[index];
        const operator = operators?.[index];
        newParams = remove(index, newParams);
        if (fieldName) {
          newParams = add(newParams, fieldName, operator, undefined);
        }
      } else {
        newParams = exchange(key, text, index, newParams);
      }

      if (areAllFieldsSetInParams(newParams)) {
        inputRef.current?.blur();
        setIsFocused(false);
      } else {
        inputRef.current?.focus();
        setIsFocused(true);
      }

      setLocalQueryParams(newParams);
      redirectWithParams({
        params: newParams,
      });
    },
    [
      redirectWithParams,
      defaultOperatorsForFields,
      allCurrentAndLocalQueryParams,
      setIsFocused,
      fieldNames,
      operators,
    ]
  );

  const clearParamKeys = useCallback(
    (keys: string[], index: number) => {
      let newParams = { ...allCurrentAndLocalQueryParams };

      for (const key of keys) {
        newParams = exchange(key, undefined, index, newParams);
      }

      setLocalQueryParams(newParams);
      redirectWithParams({
        params: newParams,
      });
    },
    [redirectWithParams, setLocalQueryParams, allCurrentAndLocalQueryParams]
  );

  const handleFocus = useCallback(() => {
    if (blurTimeoutRef.current) {
      clearTimeout(blurTimeoutRef.current);
    }
    setIsFocused(true);
  }, []);

  const handleBlur = useCallback(() => {
    blurTimeoutRef.current = setTimeout(() => {
      setIsFocused(false);
    }, 200);
  }, []);

  const handleInputChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      setText(event.target.value);
    },
    []
  );

  const lastFieldName = useMemo(
    () => findLastFieldName(fieldNames),
    [fieldNames]
  );

  const handleKeyDown = useCallback(
    (event: React.KeyboardEvent) => {
      const lastDefinedKey = findLastDefinedKey(fieldNames, operators, values);

      if (event.key === 'Escape') {
        inputRef.current?.blur();
        setIsFocused(false);
        return;
      }

      if (event.key === 'Backspace' && text === '' && !lastDefinedKey) {
        inputRef.current?.blur();
        setIsFocused(false);
        return;
      }

      if (event.key === 'Backspace' && text === '' && !!lastDefinedKey) {
        event.preventDefault();

        if (lastDefinedKey === SearchFieldParam.Operators) {
          clearParamKeys(
            [SearchFieldParam.Operators, SearchFieldParam.FieldNames],
            currentIndex
          );
          return;
        }

        setParam(lastDefinedKey, undefined, currentIndex);
        return;
      }

      if (event.key !== 'Enter') return;

      if (!text || !currentParamToEnter) return;
      const hints = findHints(currentParamToEnter, lastFieldName, searchFields);

      if (
        !hints ||
        hints.length === 0 ||
        currentParamToEnter === SearchFieldParam.Values
      ) {
        setParam(currentParamToEnter, text, activeIndex);
        setText('');
        return;
      }

      const matchedHint = hints.find((hint) =>
        hint.toLowerCase().includes(text.toLowerCase())
      );

      if (!matchedHint) return;

      setParam(currentParamToEnter, matchedHint, activeIndex);
      setText('');
    },
    [
      activeIndex,
      currentParamToEnter,
      lastFieldName,
      searchFields,
      clearParamKeys,
      setParam,
      text,
      currentIndex,
      fieldNames,
      operators,
      values,
    ]
  );

  const onClear = useCallback(() => {
    setLocalQueryParams({});
    setText('');
    setIsFocused(false);
    const clearedParams = parameters.reduce(
      (acc, param) => {
        acc[param] = undefined;
        return acc;
      },
      {} as Record<string, undefined>
    );

    redirectWithParams({ params: clearedParams });
  }, [redirectWithParams]);

  const isClearButtonHidden = numberOfParametersEntered === 0 && !text;

  const currentHints = useMemo(
    () =>
      findAndFilterHints(
        currentParamToEnter,
        lastFieldName,
        searchFields,
        text
      ),
    [currentParamToEnter, lastFieldName, searchFields, text]
  );

  const parametersForBadges = useMemo(
    () => findParametersForBadges(fieldNames, operators, values),
    [fieldNames, operators, values]
  );

  return (
    <div
      className={cx(
        'relative flex flex-row items-center justify-between rounded-[2px] bg-white px-2.5 font-lato gap-2',
        isFocused
          ? 'border-[2px] border-gray-900 -m-[1px]'
          : 'border-[1px] border-gray-200',
        className
      )}
    >
      <div className='flex flex-row w-full h-full justify-start items-center'>
        <div className='flex w-max h-max mr-1'>
          <SearchRegular className='w-4 h-4 my-2 text-gray-500' />
        </div>

        {!!parametersForBadges &&
          parametersForBadges.map((parameters, index) => (
            <TaskRunSearchFieldParametersBadges
              key={index}
              index={index}
              parameters={parameters}
              setParam={setParam}
              onClear={() =>
                clearParamKeys(
                  [
                    SearchFieldParam.FieldNames,
                    SearchFieldParam.Operators,
                    SearchFieldParam.Values,
                  ],
                  index
                )
              }
              searchFields={searchFields}
            />
          ))}

        <div className='flex flex-col w-full'>
          <TaskRunSearchFieldInput
            inputRef={inputRef}
            text={text}
            handleInputChange={handleInputChange}
            handleKeyDown={handleKeyDown}
            handleFocus={handleFocus}
            handleBlur={handleBlur}
            isEmpty={numberOfParametersEntered === 0 && !text}
            showBorder={currentParamToEnter === SearchFieldParam.Values}
          />
          <TaskRunSearchFieldHints
            options={currentHints}
            isVisible={isFocused && !!currentHints && currentHints?.length > 0}
            onSelect={(text) => {
              if (blurTimeoutRef.current) {
                clearTimeout(blurTimeoutRef.current);
              }
              setParam(currentParamToEnter, text, activeIndex);
            }}
          />
        </div>
      </div>

      <div
        className={cx(
          'cursor-pointer rounded-full bg-gray-500 flex items-center justify-center min-w-4 min-h-4 w-max h-max',
          isClearButtonHidden && 'hidden'
        )}
      >
        <DismissFilled className='w-2.5 h-2.5 text-white' onClick={onClear} />
      </div>
    </div>
  );
}
