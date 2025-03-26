'use client';

import { useMemo } from 'react';
import useMeasure from 'react-use-measure';
import { AIProviderSVGIcon } from '@/components/icons/models/AIProviderIcon';

export const DynamicTextBadge: React.FC<{
  x: number;
  y: number;
  text: string;
  environment?: string;
  providerId?: string;
  isBest: boolean;
}> = ({ x, y, text, environment, providerId, isBest }) => {
  const [textRef, { width: textWidth }] = useMeasure();
  const [environmentTextRef, { width: environmentTextWidth }] = useMeasure();

  const largeMargin = 7;
  const innerMargin = 5;
  const imageSize = 18;

  const width = useMemo(() => {
    if (!environment) {
      return largeMargin + imageSize + innerMargin + textWidth + largeMargin;
    }

    return largeMargin + imageSize + innerMargin + textWidth + innerMargin * 2 + environmentTextWidth + innerMargin + 2;
  }, [textWidth, environmentTextWidth, environment]);

  const environmentOriginX = useMemo(() => {
    return -width / 2 + largeMargin + imageSize + innerMargin + textWidth + innerMargin * 2;
  }, [width, textWidth]);

  return (
    <g transform={`translate(${x}, ${y})`}>
      <rect x={-width / 2} y={-13} width={width} height={26} fill={isBest ? '#22C55E' : '#6B7280'} rx={2} ry={2} />

      {!!providerId && (
        <g
          transform={`translate(${-width / 2 + largeMargin}, -8) scale(0.9)`}
          width={imageSize}
          height={imageSize}
          className='text-white'
        >
          <AIProviderSVGIcon providerId={providerId} />
        </g>
      )}

      <text
        ref={textRef}
        x={-width / 2 + largeMargin + imageSize + innerMargin}
        y={0.5}
        textAnchor='right'
        fill='#ffffff'
        fontSize='12'
        fontWeight='600'
        dy='.35em'
      >
        {text}
      </text>

      {!!environment && (
        <g>
          <rect
            x={environmentOriginX - innerMargin}
            y={-10}
            width={environmentTextWidth + innerMargin * 2}
            height={20}
            fill={isBest ? '#15803D' : '#374151'}
            rx={2}
            ry={2}
          />

          <text
            ref={environmentTextRef}
            x={environmentOriginX}
            y={0.5}
            textAnchor='right'
            fill='#ffffff'
            fontSize='12'
            fontWeight='600'
            dy='.35em'
          >
            {environment}
          </text>
        </g>
      )}
    </g>
  );
};
