import { CopyIcon } from 'lucide-react';
import { useCallback } from 'react';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { nightOwl } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import { useCopyToClipboard } from 'usehooks-ts';
import { Button } from './ui/Button';
import { displaySuccessToaster } from './ui/Sonner';

type CodeBlockProps = {
  language: string;
  snippet: string;
  showCopyButton?: boolean;
};

export function CodeBlock(props: CodeBlockProps) {
  const { language, snippet, showCopyButton = true } = props;
  const [, copy] = useCopyToClipboard();

  const onCopy = useCallback(() => {
    copy(snippet);
    displaySuccessToaster('Copied to clipboard');
  }, [copy, snippet]);

  return (
    <>
      <div className='rounded-lg min-w-[200px] overflow-hidden flex-shrink-0'>
        <div className='w-full bg-slate-700 pl-4 pr-1 py-1 flex items-center justify-between text-slate-50 text-sm font-mono'>
          {language}
          {showCopyButton && <Button variant='ghost' icon={<CopyIcon size={16} />} onClick={onCopy} />}
        </div>
        <SyntaxHighlighter className='!px-4 text-sm' language={language} style={nightOwl}>
          {snippet}
        </SyntaxHighlighter>
      </div>
    </>
  );
}
