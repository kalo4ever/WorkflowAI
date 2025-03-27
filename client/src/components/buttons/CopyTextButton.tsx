'use client';

import { cx } from 'class-variance-authority';
import { Check, Copy } from 'lucide-react';
import { ReactNode, useCallback, useState } from 'react';
import { useCopy } from '@/lib/hooks/useCopy';
import { Button } from '../ui/Button';

const SHORT_TEXT_THRESHOLD = 35;

type CopyContentButtonProps = {
  text: string;
  className?: string;
};

export function CopyContentButton(props: CopyContentButtonProps) {
  const { text, className } = props;
  const copyText = useCopy();
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(() => {
    copyText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000); // Reset after 2 seconds
  }, [text, copyText]);

  return (
    <Button
      variant='newDesign'
      onClick={handleCopy}
      className={cx('h-5 w-5 p-0', className)}
      data-testid='copy-button-inside'
      icon={copied ? <Check size={12} strokeWidth={2} /> : <Copy size={12} strokeWidth={2} />}
    />
  );
}

type CopyButtonWrapperProps = {
  children: ReactNode;
  text: string;
  showCopyButton?: boolean;
};

export function CopyButtonWrapper({ children, text, showCopyButton = true }: CopyButtonWrapperProps) {
  const isShortText = text.length < SHORT_TEXT_THRESHOLD;
  return (
    <div className='group flex items-center relative gap-1'>
      {children}
      {showCopyButton && (
        <CopyContentButton
          text={text}
          className={cx('opacity-0 group-hover:opacity-90', !isShortText && 'absolute top-1 right-1')}
        />
      )}
    </div>
  );
}
