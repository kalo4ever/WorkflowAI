'use client';

import { ResponsiveScatterPlot, ScatterPlotCustomSvgLayer, ScatterPlotLayerProps } from '@nivo/scatterplot';
import { Dictionary } from 'lodash';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { cn } from '@/lib/utils';
import { environmentsForVersion, formatSemverVersion, getEnvironmentShorthandName } from '@/lib/versionUtils';
import { VersionResult, VersionV1 } from '@/types/workflowAI';
import { DynamicTextBadge } from './DynamicTextBadge';
import { BenchmarkBestPicks, findScore } from './utils';

type Node = {
  id: string;
  x: number;
  y: number;
  iteration: number;
  version: string;
  environment?: string;
  isBest: boolean;
  providerId?: string;
};

type CustomScatterPlotLayerProps = ScatterPlotLayerProps<Node>;

type CustomPointsLayerProps = CustomScatterPlotLayerProps & {
  setActiveNode: React.Dispatch<React.SetStateAction<Node | undefined>>;
};

const CustomPointsLayer: React.FC<CustomPointsLayerProps> = ({ nodes, xScale, yScale, setActiveNode }) => {
  const updateAllActiveNodesOnEnter = useCallback(
    (point: Node) => {
      setActiveNode(point);
    },
    [setActiveNode]
  );

  const updateAllActiveNodesOnLeave = useCallback(
    (point: Node) => {
      setActiveNode((prev) => (prev?.id === point.id ? undefined : prev));
    },
    [setActiveNode]
  );

  return (
    <g>
      {nodes.map((point) => (
        <g key={point.id}>
          <circle
            cx={xScale(point.xValue)}
            cy={yScale(point.yValue)}
            r={8}
            fill='none'
            stroke={point.data.isBest ? '#22C55E' : '#6B7280'}
            strokeWidth={2}
          />
          <circle
            cx={xScale(point.xValue)}
            cy={yScale(point.yValue)}
            r={6}
            fill={point.data.isBest ? '#22C55E' : '#6B7280'}
            onMouseEnter={() => updateAllActiveNodesOnEnter(point.data)}
            onMouseLeave={() => updateAllActiveNodesOnLeave(point.data)}
          />
          <DynamicTextBadge
            key={point.id}
            x={xScale(point.xValue)}
            y={yScale(point.yValue) + 26}
            text={point.data.version}
            environment={point.data.environment}
            providerId={point.data.providerId}
            isBest={point.data.isBest}
          />
        </g>
      ))}
    </g>
  );
};

type CustomActivePointLinesLayerProps = CustomScatterPlotLayerProps & {
  activeNode: Node | undefined;
  revertedYLine?: boolean;
};

const CustomActivePointLinesLayer: React.FC<CustomActivePointLinesLayerProps> = ({
  xScale,
  yScale,
  activeNode,
  revertedYLine = false,
}) => {
  return (
    <g>
      {activeNode && (
        <>
          {revertedYLine ? (
            <line
              x1={xScale(activeNode.x)}
              y1={yScale(activeNode.y)}
              x2={xScale(activeNode.x)}
              y2={yScale(100)}
              stroke='#64748B'
              strokeWidth={1}
              strokeDasharray='3,3'
            />
          ) : (
            <line
              x1={xScale(activeNode.x)}
              y1={yScale(activeNode.y)}
              x2={xScale(activeNode.x)}
              y2={yScale(0)}
              stroke='#64748B'
              strokeWidth={1}
              strokeDasharray='3,3'
            />
          )}

          <line
            x1={xScale(activeNode.x)}
            y1={yScale(activeNode.y)}
            x2={xScale(0)}
            y2={yScale(activeNode.y)}
            stroke='#64748B'
            strokeWidth={1}
            strokeDasharray='3,3'
          />
        </>
      )}
    </g>
  );
};

type BenchmarkGraphProps = {
  kind: 'latency' | 'accuracy';
  bestOnes: BenchmarkBestPicks;
  benchmarkResultsDictionary: Map<number, VersionResult>;
  selectedIterations: Set<number> | undefined;
  versionByIteration: Dictionary<VersionV1>;
};

function getYParams(nodes: Node[], kind: BenchmarkGraphProps['kind'], showTitle: boolean = true) {
  let maxY = 0;
  let yTitle: string | undefined = '';
  let yFormat = (value: string) => value;
  switch (kind) {
    case 'latency':
      maxY = Math.max(...nodes.map((item) => item.y), 1);
      yTitle = 'Latency (in sec)';
      yFormat = (value) => `${value}s`;
      break;
    case 'accuracy':
      maxY = 100;
      yTitle = 'Accuracy (%)';
      yFormat = (value) => `${value}%`;
      break;
  }

  if (!showTitle) {
    yTitle = undefined;
  }
  return { maxY, yTitle, yFormat };
}

export function BenchmarkGraph(props: BenchmarkGraphProps) {
  const { kind, bestOnes, benchmarkResultsDictionary, selectedIterations, versionByIteration } = props;

  const data = useMemo(() => {
    const data: Node[] = [];

    const keys = Array.from(benchmarkResultsDictionary.keys());

    keys.forEach((iteration) => {
      const benchmarkResult = benchmarkResultsDictionary.get(iteration);

      if (!benchmarkResult) {
        return;
      }

      const version = versionByIteration[iteration];

      if (!version) {
        return;
      }

      const versionText = formatSemverVersion(version);

      if (!versionText) {
        return;
      }

      if (!!selectedIterations && !!benchmarkResult.iteration && !selectedIterations.has(benchmarkResult.iteration)) {
        return;
      }

      const environments = environmentsForVersion(version);
      const environmentName = getEnvironmentShorthandName(environments?.[0]);

      if (!benchmarkResult.average_cost_usd) {
        return;
      }

      const originX: number = benchmarkResult.average_cost_usd * 1000;
      let originY: number = 0;
      let isBest = false;

      switch (kind) {
        case 'latency':
          if (!benchmarkResult.average_duration_seconds) {
            return;
          }
          originY = benchmarkResult.average_duration_seconds;
          isBest = bestOnes.bestDurationVersions.includes(iteration);
          break;
        case 'accuracy':
          const score = findScore(benchmarkResult);
          originY = Math.round(score * 100);
          isBest = bestOnes.bestScoreVersions.includes(iteration);
          break;
      }

      const provider = benchmarkResult?.properties.provider ?? undefined;

      data.push({
        id: versionText,
        x: originX,
        y: originY,
        iteration: iteration,
        version: versionText,
        environment: environmentName,
        isBest: isBest,
        providerId: provider,
      });
    });

    const maxX = Math.max(...data.map((item) => item.x), 1);

    return [
      {
        id: 'tasks',
        data: data,
        maxX: maxX,
        ...getYParams(data, kind),
      },
    ];
  }, [bestOnes, kind, benchmarkResultsDictionary, selectedIterations, versionByIteration]);

  const [activeNode, setActiveNode] = useState<Node | undefined>(undefined);

  useEffect(() => {
    if (!selectedIterations || !activeNode) {
      return;
    }

    if (!selectedIterations.has(activeNode.iteration)) {
      setActiveNode(undefined);
    }
  }, [activeNode, selectedIterations]);

  const customActivePointLinesLayer = useMemo(() => {
    function CustomLayerGen(props: CustomActivePointLinesLayerProps) {
      const result = (
        <CustomActivePointLinesLayer {...props} activeNode={activeNode} revertedYLine={kind !== 'latency'} />
      );

      return result;
    }
    return CustomLayerGen;
  }, [activeNode, kind]);

  const customPointsLayer = useMemo(() => {
    function CustomLayerGen(props: CustomPointsLayerProps) {
      const result = <CustomPointsLayer {...props} setActiveNode={setActiveNode} />;

      return result;
    }
    return CustomLayerGen;
  }, [setActiveNode]);

  const topLabel = (
    <div className='flex w-full items-center justify-center text-gray-700 text-[13px] font-semibold pt-2 pb-3 pr-12 font-lato'>
      Price (in USD)
    </div>
  );

  const bottomLabel = (
    <div
      className={cn(
        'flex w-full items-center justify-end text-gray-700 text-[13px] font-semibold pr-2 mt-[-20px] font-lato',
        kind === 'accuracy' && 'pr-12'
      )}
    >
      <div>{kind === 'latency' ? 'Latency (in sec)' : 'Accuracy'}</div>
    </div>
  );

  return (
    <div className='flex flex-col w-full h-[456px] flex-shrink-0 pb-4 border border-gray-200 rounded-[2px]'>
      {topLabel}

      <ResponsiveScatterPlot
        theme={{
          axis: {
            ticks: {
              text: {
                fill: '#6B7280',
                fontSize: 12,
                fontFamily: 'var(--font-lato)',
              },
              line: {
                stroke: 'transparent',
              },
            },
          },
        }}
        animate={false}
        data={data}
        xScale={{
          type: 'linear',
          min: Math.floor(data[0].maxX + 1),
          max: 0,
        }}
        yScale={
          kind === 'latency'
            ? {
                type: 'linear',
                min: Math.floor(data[0].maxY + 1),
                max: 0,
              }
            : {
                type: 'linear',
                min: 0,
                max: Math.floor(data[0].maxY + 1),
              }
        }
        margin={{
          top: 20,
          right: 80,
          bottom: 40,
          left: 20,
        }}
        colors={{ scheme: 'nivo' }}
        axisTop={{
          format: (value) => `$${value}`,
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: undefined,
          legendPosition: 'middle',
          legendOffset: 0,
          ariaHidden: true,
        }}
        axisRight={{
          format: data[0].yFormat,
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: undefined,
          legendPosition: 'start',
          legendOffset: 0,
        }}
        axisBottom={{
          format: () => ``,
          tickSize: 0,
          tickPadding: 0,
          tickRotation: 0,
          legend: undefined,
          legendPosition: 'start',
          legendOffset: 0,
        }}
        axisLeft={{
          format: () => ``,
          tickSize: 0,
          tickPadding: 0,
          tickRotation: 0,
          legend: undefined,
          legendPosition: 'start',
          legendOffset: 0,
        }}
        isInteractive={false}
        useMesh={true}
        enableGridX={false}
        layers={[
          'grid',
          'axes',
          'markers',
          customActivePointLinesLayer as ScatterPlotCustomSvgLayer<Node>,
          customPointsLayer as ScatterPlotCustomSvgLayer<Node>,
        ]}
      />

      {bottomLabel}
    </div>
  );
}
