import { CheckmarkRegular, GlobeSearchRegular, WindowAdRegular } from '@fluentui/react-icons';
import { useCallback, useMemo, useState } from 'react';
import { Button } from '@/components/ui/Button';
import { SimpleTooltip } from '@/components/ui/Tooltip';
import { cn } from '@/lib/utils';
import { ToolKind } from '@/types/workflowAI';

type PlagroundParametersToolboxProps = {
  instructions: string;
  onToolsChange: (tools: ToolKind[]) => Promise<void>;
  isLoading: boolean;
};

export function PlagroundParametersToolbox(props: PlagroundParametersToolboxProps) {
  const { instructions, onToolsChange, isLoading } = props;

  const [isSearchRequested, setIsSearchRequested] = useState(false);
  const [isBrowserRequested, setIsBrowserRequested] = useState(false);

  const isSearchSelected = useMemo(() => {
    if (isLoading) {
      return isSearchRequested;
    }
    return instructions?.includes('@perplexity-sonar-pro') ?? false;
  }, [instructions, isLoading, isSearchRequested]);

  const isBrowserSelected = useMemo(() => {
    if (isLoading) {
      return isBrowserRequested;
    }
    return instructions?.includes('@browser-text') ?? false;
  }, [instructions, isLoading, isBrowserRequested]);

  const handleSearchClick = useCallback(() => {
    const tools: ToolKind[] = [];
    if (!isSearchSelected) {
      tools.push('@perplexity-sonar-pro');
    }
    if (isBrowserSelected) {
      tools.push('@browser-text');
    }
    setIsSearchRequested(!isSearchSelected);
    return onToolsChange(tools);
  }, [isBrowserSelected, isSearchSelected, onToolsChange]);

  const handleBrowserClick = useCallback(() => {
    const tools: ToolKind[] = [];
    if (!isBrowserSelected) {
      tools.push('@browser-text');
    }
    if (isSearchSelected) {
      tools.push('@perplexity-sonar-pro');
    }
    setIsBrowserRequested(!isBrowserSelected);
    return onToolsChange(tools);
  }, [isSearchSelected, isBrowserSelected, onToolsChange]);

  const searchTooltipText = useMemo(() => {
    if (isSearchSelected) {
      return 'Disabling the Search tool will prevent your task\nfrom searching Google for information.';
    }
    return 'Enabling the Search tool lets your task find up-to-date\ninformation by searching the web. Please note\nthat each Search tool usage costs $0.001.\nTasks will generally use 1-3 calls.';
  }, [isSearchSelected]);

  const browserTooltipText = useMemo(() => {
    if (isBrowserSelected) {
      return 'Disabling the Browser tool will prevent your task\nfrom fetching content from websites.';
    }
    return 'Enabling the Browser tool allows your task to fetch up-to-date\ncontent from websites. Please note that each Browser call will increases\nthe cost of running your task by $0.011. Tasks will generally use 1-3 calls.';
  }, [isBrowserSelected]);

  return (
    <div className='flex flex-row gap-2 px-3 py-2 w-full rounded-b-[2px] border-l border-r border-b border-gray-300 bg-gradient-to-b from-[#F8FAFC] to-transparent'>
      <SimpleTooltip content={searchTooltipText} tooltipClassName='whitespace-pre-line text-center'>
        <Button
          variant='newDesignGray'
          size='none'
          icon={
            isSearchSelected ? (
              <CheckmarkRegular className='w-[18px] h-[18px]' />
            ) : (
              <GlobeSearchRegular className='w-[18px] h-[18px]' />
            )
          }
          className={cn(
            'px-2 py-1.5 rounded-[2px]',
            isSearchSelected && 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200'
          )}
          onClick={handleSearchClick}
        >
          Search
        </Button>
      </SimpleTooltip>
      <SimpleTooltip content={browserTooltipText} tooltipClassName='whitespace-pre-line text-center'>
        <Button
          variant='newDesignGray'
          size='none'
          icon={
            isBrowserSelected ? (
              <CheckmarkRegular className='w-[18px] h-[18px]' />
            ) : (
              <WindowAdRegular className='w-[18px] h-[18px]' />
            )
          }
          className={cn(
            'px-2 py-1.5 rounded-[2px]',
            isBrowserSelected && 'bg-indigo-100 text-indigo-700 hover:bg-indigo-200'
          )}
          onClick={handleBrowserClick}
        >
          Browser
        </Button>
      </SimpleTooltip>
    </div>
  );
}
