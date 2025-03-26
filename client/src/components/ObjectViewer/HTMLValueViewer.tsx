import { cx } from 'class-variance-authority';
import { Expand } from 'lucide-react';
import { ChangeEvent, useCallback, useRef, useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTrigger } from '@/components/ui/Dialog';
import { Textarea } from '../ui/Textarea';
import { ReadonlyValue } from './ReadOnlyValue';
import { ValueViewerProps } from './utils';

const DEFAULT_CONTENT_HEIGHT = 100;

type PreviewIframeProps = {
  value: string;
  className?: string;
  dynamicHeight?: boolean;
};

function PreviewIframe(props: PreviewIframeProps) {
  const { value, className, dynamicHeight } = props;
  const [contentHeight, setContentHeight] = useState(DEFAULT_CONTENT_HEIGHT);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  const resizeIframe = useCallback(() => {
    if (!dynamicHeight) return;
    const scrollHeight = iframeRef.current?.contentWindow?.document?.body?.scrollHeight;
    // Sometimes, the body has no scrollHeight, so we need to set a default height
    // to avoid the iframe to be too small - we just triple the default height in that case
    if (!scrollHeight) {
      setContentHeight(3 * DEFAULT_CONTENT_HEIGHT);
    } else if (scrollHeight > DEFAULT_CONTENT_HEIGHT) {
      setContentHeight(scrollHeight);
    }
  }, [dynamicHeight]);

  if (!value) {
    return null;
  }

  return (
    <iframe
      key={value}
      srcDoc={value}
      className={cx('w-full min-h-[100px]', className)}
      style={dynamicHeight ? { height: `${contentHeight}px` } : undefined}
      ref={iframeRef}
      onLoad={resizeIframe}
    />
  );
}

export function HTMLValueViewer(props: ValueViewerProps<string>) {
  const { value, className, editable, onEdit, keyPath, showTypes } = props;
  const [open, setOpen] = useState(false);
  const onClose = useCallback(() => setOpen(false), [setOpen]);

  const onChange = useCallback(
    (e: ChangeEvent<HTMLTextAreaElement>) => {
      onEdit?.(keyPath, e.target.value);
    },
    [keyPath, onEdit]
  );

  if (showTypes) {
    return <ReadonlyValue {...props} />;
  }

  return (
    <div className='flex flex-col gap-2'>
      {!!value && (
        <div className='rounded-[2px] border border-gray-200'>
          <div className='flex items-center justify-between px-4 py-3 text-gray-600'>
            <span className='text-xs font-medium'>PREVIEW</span>
            <Dialog open={open} onOpenChange={setOpen}>
              <DialogTrigger>
                <Expand className='w-4 h-4' />
              </DialogTrigger>
              <DialogContent className='max-w-[90vw] h-[90vh] flex flex-col gap-0 p-0'>
                <DialogHeader title='Preview' onClose={onClose} />
                <div className='pl-4 flex-1'>
                  <PreviewIframe value={value} className='flex-1 h-full' />
                </div>
              </DialogContent>
            </Dialog>
          </div>
          <PreviewIframe value={value} className='max-h-[50vh]' dynamicHeight />
        </div>
      )}
      {editable && <Textarea value={value} onChange={onChange} className={cx(className, 'w-full max-h-[150px]')} />}
    </div>
  );
}
