import { useMemo } from 'react';
import { AUDIO_REF_NAME, IMAGE_REF_NAME, PDF_REF_NAME } from '@/lib/constants';
import { viewerType } from '@/lib/schemaUtils';
import { BoolValueViewer } from './BoolValueViewer';
import { DateValueViewer } from './DateValueViewer';
import { AudioValueViewer } from './FileViewers/AudioValueViewer';
import { DocumentValueViewer } from './FileViewers/DocumentValueViewer';
import { ImageValueViewer } from './FileViewers/ImageValueViewer';
import { HTMLValueViewer } from './HTMLValueViewer';
import { NumberValueViewer } from './NumberValueViewer';
import { ReadonlyValue } from './ReadOnlyValue';
import { StringValueViewer } from './StringValueViewer';
import { TimeValueViewer } from './TimeValueViewer';
import { TimezoneValueViewer } from './TimezoneValueViewer';
import { ValueViewerProps } from './utils';
import { ObjectViewer } from '..';

export function ValueViewer(props: ValueViewerProps<unknown>) {
  const {
    schema,
    value,
    referenceValue,
    originalVal,
    schemaRefName,
    columnDisplay,
    ...rest
  } = props;

  const type = useMemo(
    () => viewerType(schema, rest.defs, value),
    [value, rest.defs, schema]
  );

  const viewerProps = {
    ...rest,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    value: value as any,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    referenceValue: referenceValue as any,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    originalVal: originalVal as any,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    schema: schema as any,
  };

  if (!rest.editable) {
    if (value === undefined) {
      return (
        <ReadonlyValue
          value={value}
          schema={schema}
          // This is used when we have an Empty tag inside an object card to avoid having no padding around it
          className={columnDisplay ? 'm-2' : undefined}
          previewMode={rest.previewMode}
        />
      );
    } else if (Array.isArray(value) && value.length === 0) {
      return (
        <ReadonlyValue
          value='Empty List'
          schema={schema}
          previewMode={rest.previewMode}
        />
      );
    }
  }

  // Sometimes we don't figure out that the schema type is an image in viewerType() because it is nested in an anyOf, oneOf al allOf
  // That's why we rely on the schemaRefName
  if (schemaRefName) {
    switch (schemaRefName) {
      case IMAGE_REF_NAME:
        return <ImageValueViewer {...viewerProps} />;
      case AUDIO_REF_NAME:
        return <AudioValueViewer {...viewerProps} />;
      case PDF_REF_NAME:
        return <DocumentValueViewer {...viewerProps} />;
    }
  }

  // Sometimes during streaming, the value does not match the schema type
  if (
    schema?.type === 'string' &&
    value !== null &&
    typeof value !== 'string' &&
    !rest.editable
  ) {
    return (
      <ReadonlyValue
        value={JSON.stringify(value)}
        referenceValue={JSON.stringify(referenceValue)}
        schema={schema}
        previewMode={rest.previewMode}
      />
    );
  }

  switch (type) {
    case 'timezone':
      return <TimezoneValueViewer {...viewerProps} />;
    case 'time':
      return <TimeValueViewer {...viewerProps} />;
    case 'date':
      return <DateValueViewer {...viewerProps} />;
    case 'date-time':
      return <DateValueViewer {...viewerProps} withTimePicker />;
    case 'string':
      return <StringValueViewer {...viewerProps} />;
    case 'integer':
      return <NumberValueViewer {...viewerProps} integer />;
    case 'number':
      return <NumberValueViewer {...viewerProps} />;
    case 'boolean':
      return <BoolValueViewer {...viewerProps} />;
    case 'html':
      return <HTMLValueViewer {...viewerProps} />;
    case 'image':
      return <ImageValueViewer {...viewerProps} />;
    case 'audio':
      return <AudioValueViewer {...viewerProps} />;
    case 'document':
      return <DocumentValueViewer {...viewerProps} />;
    case 'null':
      return <ReadonlyValue {...viewerProps} value='null' />;
    case 'undefined':
      return (
        <ReadonlyValue
          {...viewerProps}
          value='undefined'
          className='bg-red-500'
        />
      );
    case 'array':
      return (
        <div className='pl-[10px] w-full'>
          <ObjectViewer {...viewerProps} isArray />
        </div>
      );
    case 'object':
      return (
        <div className='w-full'>
          <ObjectViewer {...viewerProps} />
        </div>
      );
    default:
      // TODO: sentry
      console.error('Unknown field type', props.keyPath);
      return null;
  }
}
