import { cx } from 'class-variance-authority';
import { useMemo } from 'react';
import { useParsedSearchParams } from '@/lib/queryString';
import { useSuggestedAgents } from '@/store/suggested_agents';

type Props = {
  className?: string;
};

export function HeaderSection(props: Props) {
  const { className } = props;

  const { companyURL } = useParsedSearchParams('companyURL');

  const isInitialized = useSuggestedAgents((state) =>
    companyURL ? !!state.suggestedAgentsByURL[companyURL] : false
  );

  const text = useMemo(() => {
    if (!!isInitialized && !!companyURL) {
      const capitalizedURL =
        companyURL.charAt(0).toUpperCase() + companyURL.slice(1);
      return `What AI agents can you build for ${capitalizedURL}?`;
    }

    return 'What AI agents can you build for you and your company?';
  }, [isInitialized, companyURL]);

  return (
    <div
      className={cx(
        'flex items-center justify-center w-full text-center gap-3 px-4 text-gray-900 font-medium text-[48px]',
        className
      )}
    >
      {text}
    </div>
  );
}
