import { cx } from 'class-variance-authority';
import { partition } from 'lodash';
import { ChevronDown, Eraser } from 'lucide-react';
import { useCallback } from 'react';
import { Button } from '@/components/ui/Button';
import { Checkbox } from '@/components/ui/Checkbox';
import { Command, CommandGroup, CommandItem, CommandList } from '@/components/ui/Command';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/Popover';
import { useQuery } from '@/lib/hooks';
import { taskRunQueryMapper } from '@/lib/hooks/useQuery/mappers';

type TaskRunCorrectnessColumnFilterProps = {
  autoEvaluatorName?: string;
};

function getScoreValue(score: string, autoEvaluatorName: string | undefined) {
  return `${autoEvaluatorName || 'user'}[=]${score}`;
}

export function TaskRunCorrectnessColumnFilter(props: TaskRunCorrectnessColumnFilterProps) {
  const { autoEvaluatorName } = props;
  const [query, setQuery] = useQuery(taskRunQueryMapper);
  const { score_filters = [], ...queryRest } = query;

  const [manualFilters, autoFilters] = partition(score_filters, (value) => value.startsWith('user'));
  const untouchedFilters = !!autoEvaluatorName ? manualFilters : autoFilters;
  const updatedFilters = !!autoEvaluatorName ? autoFilters : manualFilters;

  const handleSelectionChange = useCallback(
    (selectedValue: string) => {
      const newUpdatedScoreFilters = updatedFilters.includes(selectedValue) ? [] : [selectedValue];
      setQuery({
        score_filters: [...newUpdatedScoreFilters, ...untouchedFilters],
        ...queryRest,
      });
    },
    [setQuery, queryRest, untouchedFilters, updatedFilters]
  );

  const onClearFilter = useCallback(() => {
    setQuery({ score_filters: undefined });
  }, [setQuery]);

  return (
    <Popover>
      <PopoverTrigger asChild>
        <ChevronDown
          size={16}
          className={cx(
            'text-slate-500 cursor-pointer',
            updatedFilters.length > 0 ? 'border border-slate-500 rounded-full' : undefined
          )}
        />
      </PopoverTrigger>
      <PopoverContent className='w-[200px] p-3'>
        <Command>
          <CommandList>
            <CommandGroup>
              {['0', '1'].map((value) => {
                const formattedValue = getScoreValue(value, autoEvaluatorName);
                return (
                  <CommandItem
                    key={formattedValue}
                    value={formattedValue}
                    onSelect={() => handleSelectionChange(formattedValue)}
                  >
                    <Checkbox className='mr-2' checked={score_filters.includes(formattedValue)} />
                    {value}
                  </CommandItem>
                );
              })}
            </CommandGroup>
          </CommandList>
        </Command>
        <Button
          variant='outline'
          lucideIcon={Eraser}
          className='w-fit'
          onClick={onClearFilter}
          disabled={!score_filters?.length}
        >
          Clear Filter
        </Button>
      </PopoverContent>
    </Popover>
  );
}
