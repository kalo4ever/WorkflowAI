import { cx } from 'class-variance-authority';
import { ChangeEvent, useCallback, useMemo } from 'react';
import { JsonStringSchema } from '@/types';
import { Combobox } from '../ui/Combobox';
import { Input } from '../ui/Input';
import { Textarea } from '../ui/Textarea';
import { ReadonlyValue } from './ReadOnlyValue';
import { ValueViewerProps, stringifyNil } from './utils';

function EnumValueViewer(
  props: ValueViewerProps<string | null | undefined, JsonStringSchema>
) {
  const { value, className, schema, keyPath, onEdit } = props;
  const isNullable = schema?.nullable === true;
  const options = useMemo(() => {
    const choices: (string | null)[] = schema?.enum ?? [];
    if (isNullable) {
      return [null, ...choices];
    }
    return choices;
  }, [schema?.enum, isNullable]);
  const formattedOptions = useMemo(
    () =>
      options.map((option) => ({
        value: stringifyNil(option),
        label: stringifyNil(option),
      })),
    [options]
  );

  const onChange = useCallback(
    (newValue: string) => {
      if (isNullable && !newValue) {
        onEdit?.(keyPath, null);
        return;
      }
      onEdit?.(keyPath, newValue);
    },
    [isNullable, keyPath, onEdit]
  );

  return (
    <div className={cx(className, '-mt-0.5')}>
      <Combobox
        value={value ?? ''}
        options={formattedOptions}
        onChange={onChange}
      />
    </div>
  );
}

function EditableStringValueViewer(
  props: ValueViewerProps<string | null | undefined, JsonStringSchema>
) {
  const { value, className, editable, keyPath, onEdit, schema } = props;

  const onChange = useCallback(
    (e: ChangeEvent<HTMLTextAreaElement | HTMLInputElement>) => {
      onEdit?.(keyPath, e.target.value);
    },
    [keyPath, onEdit]
  );

  const isEmail = useMemo(() => schema?.format === 'email', [schema?.format]);

  const pattern = useMemo(() => {
    if (isEmail) {
      return '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$';
    }
    return schema?.pattern;
  }, [isEmail, schema?.pattern]);

  const isInvalidPattern = useMemo(() => {
    if (!pattern) {
      return false;
    }
    const re = new RegExp(pattern);
    return !re.test(value ?? '');
  }, [pattern, value]);

  const textProps = {
    value: value ?? '',
    className: cx('w-full min-w-[150px]', className, {
      'border-red-500': isInvalidPattern,
    }),
    onChange,
    disabled: !editable,
    pattern: schema?.pattern,
    type: isEmail ? 'email' : 'text',
    placeholder: schema?.description,
  };

  return (
    <div className='flex flex-col gap-1 w-full'>
      {textProps.pattern ? (
        <Input {...textProps} />
      ) : (
        <Textarea {...textProps} />
      )}
      {isInvalidPattern && (
        <p className='text-xs text-red-500'>
          {isEmail
            ? 'Value is not a valid email address'
            : `Value does not match pattern: ${pattern}`}
        </p>
      )}
    </div>
  );
}

export function StringValueViewer(
  props: ValueViewerProps<string | null | undefined, JsonStringSchema>
) {
  const { schema, editable } = props;

  if (editable && schema?.enum) {
    return <EnumValueViewer {...props} />;
  }

  if (!editable) {
    return <ReadonlyValue {...props} />;
  }

  return <EditableStringValueViewer {...props} />;
}
