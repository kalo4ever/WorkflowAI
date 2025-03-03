'use client';

import { cx } from 'class-variance-authority';
import * as React from 'react';
import { useCallback, useEffect, useMemo, useRef } from 'react';
import { Model } from '@/types/aliases';
import { ModelResponse } from '@/types/workflowAI';
import { formatAIModels } from './labels/ModelLabel';

type AIModelScrollSelectionProps = {
  value: Model | null | undefined;
  onModelChange: (value: Model) => void;
  modelOptions: ModelResponse[];
  sort: 'intelligence' | 'price' | 'latest';
};

export function AIModelScrollSelection(props: AIModelScrollSelectionProps) {
  const { value, onModelChange, modelOptions, sort } = props;

  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const optionRefs = useRef<(HTMLDivElement | null)[]>([]); // Create refs for each option

  const formattedModelOptions = useMemo(
    () => formatAIModels(modelOptions, sort),
    [modelOptions, sort]
  );

  const scrollTo = useCallback(
    (index: number, instant: boolean): Promise<void> => {
      return new Promise((resolve) => {
        const selectedOption = optionRefs.current[index];

        if (!scrollContainerRef.current || !selectedOption) {
          resolve();
          return;
        }

        const containerRect =
          scrollContainerRef.current.getBoundingClientRect();
        const optionRect = selectedOption.getBoundingClientRect();

        const margin = 8;
        const scrollOffset = optionRect.left - containerRect.left - margin;

        if (instant) {
          scrollContainerRef.current.style.scrollBehavior = 'auto';
          scrollContainerRef.current.scrollLeft += scrollOffset;
          scrollContainerRef.current.style.scrollBehavior = 'smooth';
          resolve();
          return;
        }

        scrollContainerRef.current.scrollBy({
          left: scrollOffset,
          behavior: 'smooth',
        });

        setTimeout(() => {
          resolve();
        }, 300);
      });
    },
    []
  );

  useEffect(() => {
    if (value) {
      const index = formattedModelOptions.findIndex(
        (option) => option.value === value
      );
      scrollTo(index, true);
    }
  }, [value, formattedModelOptions, scrollTo]);

  const onSelect = useCallback(
    async (selectedValue: Model, index: number) => {
      await scrollTo(index, false);

      if (selectedValue !== value) {
        onModelChange(selectedValue);
      }
    },
    [onModelChange, value, scrollTo]
  );

  return (
    <div
      ref={scrollContainerRef}
      className='flex flex-row w-full gap-1 overflow-y-clip overflow-x-auto scroll-smooth px-2'
    >
      <style>{`div::-webkit-scrollbar { display: none; }`}</style>
      {formattedModelOptions.map((option, index) => (
        <div
          key={option.value}
          ref={(element) => (optionRefs.current[index] = element)}
          className={cx(
            'border rounded-full py-2 px-4 text-sm font-medium ',
            value === option.value
              ? 'text-slate-700 bg-slate-200'
              : 'text-slate-600'
          )}
          onClick={() => onSelect(option.value as Model, index)}
        >
          {option.renderLabel({
            isSelected: value === option.value,
            showCheck: false,
          })}
        </div>
      ))}
    </div>
  );
}
