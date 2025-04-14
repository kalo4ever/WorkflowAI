import { cx } from 'class-variance-authority';
import { diffLines, diffWords } from 'diff';
import DOMPurify from 'dompurify';
import { useMemo } from 'react';
import { CopyButtonWrapper } from '@/components/buttons/CopyTextButton';
import { SimpleTooltip } from '../ui/Tooltip';
import { ValueViewerProps, stringifyNil } from './utils';

function shouldDiffLineForString(text: string) {
  return text?.includes('\n') || text?.includes(' ');
}

type ReadonlyValueContentProps = {
  className: string;
  previewMode: boolean;
  isError: boolean;
  truncateText: number;
  icon: React.ReactNode;
  text: string;
};

function ReadonlyValueContent(props: ReadonlyValueContentProps) {
  const { className, previewMode, isError, truncateText, icon, text } = props;

  const isSVG = useMemo(() => {
    if (!text) return false;
    const trimmedText = text.trim();
    return trimmedText.startsWith('<svg') && trimmedText.endsWith('</svg>');
  }, [text]);

  const sanitizedSVG = useMemo(() => {
    if (!isSVG) return null;

    // Add viewBox if not present to support width adjustments for layout
    let svgText = text;
    if (!text.includes('viewBox=')) {
      const widthMatch = text.match(/width="([^"]+)"/);
      const heightMatch = text.match(/height="([^"]+)"/);
      if (widthMatch && heightMatch) {
        const width = widthMatch[1];
        const height = heightMatch[1];
        svgText = text.replace(/<svg/, `<svg viewBox="0 0 ${width} ${height}"`);
      }
    }

    return DOMPurify.sanitize(svgText, {
      USE_PROFILES: { svg: true, svgFilters: true },
      ADD_TAGS: ['use'],
      ADD_ATTR: ['xlink:href'],
    });
  }, [text, isSVG]);

  if (isSVG && sanitizedSVG) {
    return (
      <div
        data-testid='viewer-readonly-value'
        className={cx(
          className,
          'relative min-h-6 px-1.5 py-0.5 border border-gray-200 rounded-[2px] flex items-center w-full',
          previewMode ? 'bg-gray-50' : 'bg-white'
        )}
      >
        <div className='flex-1 w-full overflow-hidden'>
          <div
            className='w-full [&>svg]:block [&>svg]:w-full [&>svg]:h-auto [&>svg]:max-w-full'
            style={{
              width: '100%',
              height: 'auto',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
            }}
            dangerouslySetInnerHTML={{ __html: sanitizedSVG }}
          />
        </div>
        {!!icon && <div className='flex-shrink-0 ml-1'>{icon}</div>}
      </div>
    );
  }

  return (
    <div
      data-testid='viewer-readonly-value'
      className={cx(
        className,
        'relative min-h-6 font-medium text-[13px] px-1.5 py-0.5 border border-gray-200 rounded-[2px] flex items-center',
        previewMode ? 'bg-gray-50' : 'bg-white',
        {
          'text-gray-400': !isError && previewMode,
          'text-gray-700': !isError && !previewMode,
          'text-red-600 border-red-200': isError,
        }
      )}
    >
      <div
        className={cx('flex-1', !!truncateText && 'overflow-hidden')}
        style={{
          display: !!truncateText ? '-webkit-box' : 'block',
          WebkitLineClamp: !!truncateText ? truncateText : undefined,
          WebkitBoxOrient: !!truncateText ? 'vertical' : undefined,
          wordBreak: 'break-word',
          overflowWrap: 'anywhere',
        }}
      >
        {text}
      </div>
      {!!icon && <div className='flex-shrink-0 ml-1'>{icon}</div>}
    </div>
  );
}

type ReadonlyValueProps = Pick<
  ValueViewerProps<string | number | boolean | null | undefined>,
  | 'value'
  | 'referenceValue'
  | 'className'
  | 'schema'
  | 'isError'
  | 'showTypes'
  | 'previewMode'
  | 'showDescriptionExamples'
  | 'hideCopyValue'
  | 'truncateText'
> & {
  icon?: React.ReactNode;
};

export function ReadonlyValue(props: ReadonlyValueProps) {
  const {
    value,
    referenceValue,
    className,
    isError,
    showTypes,
    icon,
    previewMode,
    showDescriptionExamples,
    hideCopyValue,
    truncateText,
  } = props;
  const text = stringifyNil(value);

  const shouldDiffLine = useMemo(() => {
    if (!referenceValue || typeof referenceValue !== 'string') {
      return false;
    }
    return shouldDiffLineForString(referenceValue) || shouldDiffLineForString(text);
  }, [referenceValue, text]);

  const diff = useMemo(() => {
    if (!referenceValue || typeof referenceValue !== 'string') {
      return null;
    }
    return shouldDiffLine ? diffLines(referenceValue, text) : diffWords(referenceValue, text);
  }, [text, referenceValue, shouldDiffLine]);

  if (diff) {
    return (
      <div
        className={cx(
          'w-full flex gap-x-1 gap-y-0.5 flex-wrap border border-gray-200 bg-white rounded-[2px] text-[13px] font-medium px-1.5 py-0.5 text-gray-700',
          shouldDiffLine ? 'flex-col items-start' : 'items-center'
        )}
      >
        {diff.map((part) => (
          <span
            key={part.value}
            className={cx('shrink-0 whitespace-break-spaces', {
              'bg-green-100': part.added,
              'bg-red-100': part.removed,
            })}
          >
            {part.value}
          </span>
        ))}
      </div>
    );
  }

  const content = (
    <ReadonlyValueContent
      text={text}
      className={className ?? ''}
      previewMode={previewMode ?? false}
      isError={isError ?? false}
      truncateText={truncateText ?? 0}
      icon={icon}
    />
  );

  if (!!showTypes) {
    return content;
  }

  if (!showTypes && !!showDescriptionExamples && (value === null || value === 'null')) {
    return null;
  }

  if (!!previewMode) {
    return (
      <SimpleTooltip
        content={`This is example data only. You will be able test with more\nrelevant, custom content on Playground after saving your\nschema.`}
        tooltipDelay={200}
        tooltipClassName='whitespace-break-spaces text-center'
      >
        <div className='group flex items-center relative gap-1'>{content}</div>
      </SimpleTooltip>
    );
  }

  if (hideCopyValue) {
    return <div className='group flex items-center gap-1'>{content}</div>;
  }

  return <CopyButtonWrapper text={text}>{content}</CopyButtonWrapper>;
}
