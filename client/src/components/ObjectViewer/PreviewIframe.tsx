import { cx } from 'class-variance-authority';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useToggle } from 'usehooks-ts';

const DEFAULT_CONTENT_HEIGHT = 100;

type PreviewIframeProps = {
  value: string;
  className?: string;
  dynamicHeight?: boolean;
};

export function PreviewIframe(props: PreviewIframeProps) {
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

  const [mainValue, setMainValue] = useState<string | undefined>(undefined);
  const [secondaryValue, setSecondaryValue] = useState<string | undefined>(undefined);
  const [showSecondaryIframe, setShowSecondaryIframe] = useState(false);

  const [isRendering, setIsRendering] = useState(false);

  const currentRenderingValueRef = useRef(value);
  const currentMainValueRef = useRef(mainValue);
  currentMainValueRef.current = mainValue;

  useEffect(() => {
    // For first render let's just display the value
    if (!currentMainValueRef.current) {
      setMainValue(value);
      return;
    }

    if (isRendering) return;
    if (currentMainValueRef.current === value) return;

    setIsRendering(true);
    currentRenderingValueRef.current = value;

    setSecondaryValue(currentRenderingValueRef.current);
    // We need to wait for the secondary iframe to be rendered before we can swap the main iframe
    setTimeout(() => {
      setShowSecondaryIframe(true);

      // Now let's do the same for the main iframe
      setMainValue(currentRenderingValueRef.current);
      setTimeout(() => {
        setShowSecondaryIframe(false);
        setIsRendering(false);
      }, 1000);
    }, 1000);
  }, [value, isRendering]);

  if (!value) {
    return null;
  }

  return (
    <div className={cx('w-full min-h-[100px] relative', className)}>
      {isRendering && (
        <iframe
          key={secondaryValue + '1'}
          srcDoc={secondaryValue}
          className={cx('w-full min-h-[100px] absolute top-0 left-0', className)}
          style={{ height: dynamicHeight ? `${contentHeight}px` : undefined, opacity: showSecondaryIframe ? 1 : 0 }}
        />
      )}
      <iframe
        key={mainValue + '0'}
        srcDoc={mainValue}
        className={cx('w-full min-h-[100px]', className)}
        style={{ height: dynamicHeight ? `${contentHeight}px` : undefined, opacity: showSecondaryIframe ? 0 : 1 }}
        ref={iframeRef}
        onLoad={resizeIframe}
      />
    </div>
  );
}
