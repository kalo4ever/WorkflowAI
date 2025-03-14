import { Copy16Regular } from '@fluentui/react-icons';
import { useCallback } from 'react';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { xcode } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import { useCopyToClipboard } from 'usehooks-ts';
import { Button } from '@/components/ui/Button';
import { displaySuccessToaster } from '@/components/ui/Sonner';
import { PageSection } from './PageSection';

type CodeBlockProps = {
  title?: string;
  language?: string;
  snippet: string;
  showCopyButton?: boolean;
  showTopBorder?: boolean;
};

export function CodeBlock(props: CodeBlockProps) {
  const {
    title,
    language,
    snippet,
    showCopyButton = true,
    showTopBorder,
  } = props;
  const [, copy] = useCopyToClipboard();

  const onCopy = useCallback(() => {
    copy(snippet);
    displaySuccessToaster('Copied to clipboard');
  }, [copy, snippet]);

  return (
    <div className='flex flex-col w-full h-max'>
      <PageSection
        title={title ?? language ?? ''}
        showTopBorder={showTopBorder}
      >
        {showCopyButton && (
          <Button
            variant='newDesign'
            icon={<Copy16Regular />}
            onClick={onCopy}
            className='w-7 h-7 px-0 py-0'
          />
        )}
      </PageSection>
      <SyntaxHighlighter
        className='!px-4 flex w-full h-max font-mono text-xs'
        language={language}
        style={xcode}
      >
        {snippet}
      </SyntaxHighlighter>
    </div>
  );
}
