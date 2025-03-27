import { cx } from 'class-variance-authority';
import { cloneDeep } from 'lodash';
import { Plus, Trash2 } from 'lucide-react';
import { useCallback, useMemo } from 'react';
import { useToggle } from 'usehooks-ts';
import { SimpleTooltip } from '@/components/ui/Tooltip';
import { SchemaEditorField, SelectableFieldType, shouldDisableRemove } from '@/lib/schemaEditorUtils';
import { Button } from '../ui/Button';
import { EnumMultiSelect } from '../ui/EnumMultiSelect';
import { DynamicWidthInput } from './DynamicWidthInput';
import { FieldTypeIcon } from './FieldTypeIcon';
import { RootObjectListSwitch } from './RootObjectListSwitch';
import { SchemaObjectCard } from './SchemaObjectCard';
import { SchemaSplattedSection } from './SchemaSplattedSection';
import { SchemaTypeSelector } from './SchemaTypeSelector';

type SchemaEditorFieldLabelProps = {
  splattedSchema: SchemaEditorField;
  onFieldRemove: (() => void) | undefined;
  onFieldKeyChange: (newKey: string) => void;
  onFieldTypeChange: (newType: SelectableFieldType) => void;
  onArrayFieldTypeChange: (newType: SelectableFieldType) => void;
  toggleCollapse: () => void;
  disableImage: boolean;
  disableAudio: boolean;
  disableDocuments: boolean;
};

function SchemaEditorFieldLabel(props: SchemaEditorFieldLabelProps) {
  const {
    splattedSchema,
    onFieldRemove,
    onFieldKeyChange,
    onFieldTypeChange,
    onArrayFieldTypeChange,
    toggleCollapse,
    disableImage,
    disableAudio,
    disableDocuments,
  } = props;

  const { keyName, type, arrayType } = splattedSchema;

  return (
    <div className='w-full flex items-center gap-2 p-2 hover:bg-gray-100 transition-colors rounded-[2px] group font-lato'>
      <FieldTypeIcon type={type} onClick={toggleCollapse} />
      <DynamicWidthInput value={keyName} onChange={onFieldKeyChange} className='w-fit' placeholder='Enter field' />
      <div className='text-gray-500 text-sm font-medium -translate-x-1'>:</div>
      <SchemaTypeSelector
        type={type}
        onChange={onFieldTypeChange}
        disableImage={disableImage}
        disableAudio={disableAudio}
        disableDocuments={disableDocuments}
      />
      {!!arrayType && (
        <>
          <div className='text-slate-500 text-sm'>of</div>
          <SchemaTypeSelector
            type={arrayType}
            onChange={onArrayFieldTypeChange}
            noArray
            disableImage={disableImage}
            disableAudio={disableAudio}
            disableDocuments={disableDocuments}
          />
        </>
      )}
      <SimpleTooltip content={!onFieldRemove ? 'You need at least one field in an object' : undefined}>
        <Trash2
          size={16}
          className={cx(
            'text-gray-500 invisible group-hover:visible',
            !!onFieldRemove ? 'cursor-pointer' : 'cursor-not-allowed'
          )}
          onClick={onFieldRemove}
        />
      </SimpleTooltip>
    </div>
  );
}

const DEFAULT_FIELD: SchemaEditorField = {
  keyName: 'unnamed_field',
  type: 'string',
};
const DEFAULT_ENUM_VALUES = ['value1', 'value2', 'value3'];

type SchemaEditorFieldContentProps = {
  splattedSchema: SchemaEditorField;
  setSplattedSchema: (splattedSchema: SchemaEditorField | undefined) => void;
  isRoot: boolean;
  isRootObject: boolean;
  disableImage: boolean;
  disableAudio: boolean;
  disableDocuments: boolean;
};

function SchemaEditorFieldContent(props: SchemaEditorFieldContentProps) {
  const { splattedSchema, setSplattedSchema, isRoot, isRootObject, disableImage, disableAudio, disableDocuments } =
    props;
  const { keyName, type, fields, arrayType } = splattedSchema;

  const enumValues = useMemo(() => {
    if (type === 'enum') {
      return splattedSchema.enum;
    } else if (arrayType === 'enum' && !!fields && fields.length > 0) {
      return fields?.[0].enum;
    }
    return undefined;
  }, [type, arrayType, splattedSchema.enum, fields]);

  const handleSetSplattedSchema = useCallback(
    (newField: SchemaEditorField | undefined, index: number) => {
      if (!fields) {
        return;
      }
      const newSplattedSchema = {
        ...cloneDeep(splattedSchema),
        fields: fields.map((field, i) => (i === index ? newField : field)).filter((f) => !!f) as SchemaEditorField[],
      };
      setSplattedSchema(newSplattedSchema);
    },
    [fields, splattedSchema, setSplattedSchema]
  );

  const onAddField = useCallback(() => {
    const newSplattedSchema = {
      ...cloneDeep(splattedSchema),
      fields: [...(fields || []), DEFAULT_FIELD],
    };
    setSplattedSchema(newSplattedSchema);
  }, [fields, splattedSchema, setSplattedSchema]);

  const disableRemove = useMemo(() => shouldDisableRemove(splattedSchema), [splattedSchema]);

  const onEnumUpdate = useCallback(
    (newEnumValues: string[]) => {
      let newSplattedSchema: SchemaEditorField = cloneDeep(splattedSchema);
      if (type === 'enum') {
        newSplattedSchema = {
          ...newSplattedSchema,
          enum: newEnumValues,
        };
      } else if (arrayType === 'enum') {
        newSplattedSchema = {
          ...newSplattedSchema,
          fields: [
            {
              keyName: '',
              type: 'enum',
              enum: newEnumValues,
            },
          ],
        };
      }
      setSplattedSchema(newSplattedSchema);
    },
    [splattedSchema, setSplattedSchema, type, arrayType]
  );

  const commonWrapperClassName = 'pl-10';

  if (type === 'object' || arrayType === 'object') {
    const content = (
      <div className='flex flex-col'>
        {(fields || []).map((field, index) => (
          // We need to call SchemaSplattedEditor recursively so we can mute the linter here
          // eslint-disable-next-line no-use-before-define
          <InnerSchemaSplattedEditor
            key={`${keyName}-${index}`}
            splattedSchema={field}
            setSplattedSchema={(newField: SchemaEditorField | undefined) => handleSetSplattedSchema(newField, index)}
            disableRemove={disableRemove}
            disableImage={disableImage}
            disableAudio={disableAudio}
            disableDocuments={disableDocuments}
            isRootObject={isRootObject}
          />
        ))}
      </div>
    );

    return !isRoot ? (
      <SchemaObjectCard onAddField={onAddField} className={commonWrapperClassName}>
        {content}
      </SchemaObjectCard>
    ) : (
      <div className='flex flex-col gap-2'>
        {content}
        {onAddField && (
          <Button
            lucideIcon={Plus}
            variant='subtle'
            onClick={onAddField}
            className='w-fit rounded-[2px] bg-gray-100 hover:bg-gray-200 text-gray-500 text-sm font-semibold font-lato ml-2'
          >
            Add New Field
          </Button>
        )}
      </div>
    );
  } else if ((type === 'enum' || arrayType === 'enum') && !!enumValues) {
    return <EnumMultiSelect onChange={onEnumUpdate} enumValues={enumValues} className={commonWrapperClassName} />;
  }
  return null;
}

type InnerSchemaSplattedEditorProps = {
  splattedSchema: SchemaEditorField | undefined;
  setSplattedSchema: (splattedSchema: SchemaEditorField | undefined) => void;
  isRoot?: boolean;
  disableRemove?: boolean;
  disableImage?: boolean;
  disableAudio?: boolean;
  disableDocuments?: boolean;
  isRootObject: boolean;
  contentRef?: React.LegacyRef<HTMLDivElement>;
};

function InnerSchemaSplattedEditor(props: InnerSchemaSplattedEditorProps) {
  const {
    splattedSchema,
    setSplattedSchema,
    isRoot = false,
    disableRemove = false,
    disableImage = false,
    disableAudio = false,
    disableDocuments = false,
    isRootObject,
    contentRef,
  } = props;
  const keyName = splattedSchema?.keyName;

  const onFieldKeyChange = useCallback(
    (newKey: string) => {
      if (!splattedSchema) {
        return;
      }
      const newSplattedSchema = {
        ...cloneDeep(splattedSchema),
        keyName: newKey,
      };
      setSplattedSchema(newSplattedSchema);
    },
    [setSplattedSchema, splattedSchema]
  );

  const onFieldTypeChange = useCallback(
    (newType: SelectableFieldType) => {
      let newSplattedSchema: SchemaEditorField = {
        keyName: keyName || '',
        type: newType,
        fields: undefined,
        enum: newType === 'enum' ? DEFAULT_ENUM_VALUES : undefined,
      };
      if (newType === 'array') {
        newSplattedSchema = {
          ...newSplattedSchema,
          arrayType: 'string',
          fields: [DEFAULT_FIELD],
        };
      } else if (newType === 'object') {
        newSplattedSchema = {
          ...newSplattedSchema,
          fields: [DEFAULT_FIELD],
        };
      }
      setSplattedSchema(newSplattedSchema);
    },
    [setSplattedSchema, keyName]
  );

  const onArrayFieldTypeChange = useCallback(
    (newType: SelectableFieldType) => {
      if (splattedSchema?.type !== 'array') {
        return;
      }
      let newSplattedSchema: SchemaEditorField = {
        ...cloneDeep(splattedSchema),
        arrayType: newType,
        fields: [
          {
            keyName: '',
            type: newType,
            enum: newType === 'enum' ? DEFAULT_ENUM_VALUES : undefined,
          },
        ],
      };
      if (newType === 'object') {
        newSplattedSchema = {
          ...newSplattedSchema,
          fields: [DEFAULT_FIELD],
        };
      }
      setSplattedSchema(newSplattedSchema);
    },
    [splattedSchema, setSplattedSchema]
  );

  const onFieldRemove = useCallback(() => {
    setSplattedSchema(undefined);
  }, [setSplattedSchema]);

  const [collapsed, toggleCollapse] = useToggle(false);

  if (!splattedSchema) {
    return null;
  }

  return (
    <div className='min-w-full flex flex-col w-fit gap-1 p-2 overflow-x-auto' ref={contentRef}>
      {!isRoot && (
        <SchemaEditorFieldLabel
          splattedSchema={splattedSchema}
          onFieldRemove={disableRemove ? undefined : onFieldRemove}
          onFieldKeyChange={onFieldKeyChange}
          onFieldTypeChange={onFieldTypeChange}
          onArrayFieldTypeChange={onArrayFieldTypeChange}
          toggleCollapse={toggleCollapse}
          disableImage={disableImage}
          disableAudio={disableAudio}
          disableDocuments={disableDocuments}
        />
      )}
      {!collapsed && (
        <SchemaEditorFieldContent
          splattedSchema={splattedSchema}
          setSplattedSchema={setSplattedSchema}
          isRoot={isRoot}
          isRootObject={isRootObject}
          disableImage={disableImage}
          disableAudio={disableAudio}
          disableDocuments={disableDocuments}
        />
      )}
    </div>
  );
}

type SchemaSplattedEditorProps = Pick<
  InnerSchemaSplattedEditorProps,
  'splattedSchema' | 'setSplattedSchema' | 'disableImage' | 'disableAudio' | 'disableDocuments'
> & {
  className?: string;
  title: string;
  details?: string;
  style?: React.CSSProperties;
  contentRef?: React.LegacyRef<HTMLDivElement>;
};

export function SchemaSplattedEditor(props: SchemaSplattedEditorProps) {
  const {
    splattedSchema,
    setSplattedSchema,
    disableImage,
    disableAudio,
    disableDocuments,
    className,
    title,
    details,
    style,
    contentRef,
  } = props;

  const isRootObject = useMemo(
    () =>
      !splattedSchema ||
      !splattedSchema.fields ||
      splattedSchema.fields.length !== 1 ||
      splattedSchema.fields[0].type !== 'array' ||
      splattedSchema.fields[0].arrayType !== 'object',
    [splattedSchema]
  );

  const toggleRootObjectList = useCallback(() => {
    if (!splattedSchema || splattedSchema.keyName !== '') {
      return;
    }
    let { fields } = splattedSchema;
    if (!fields || fields.length === 0) {
      return;
    }
    if (isRootObject) {
      fields = [
        {
          keyName: 'list',
          type: 'array',
          arrayType: 'object',
          fields: splattedSchema.fields,
        },
      ];
    } else {
      const field = fields[0];
      const innerFields = field.fields;
      if (!innerFields || innerFields.length === 0) {
        return;
      }
      fields = innerFields;
    }
    const newSplattedSchema: SchemaEditorField = {
      ...cloneDeep(splattedSchema),
      arrayType: isRootObject ? 'object' : undefined,
      fields,
    };
    setSplattedSchema(newSplattedSchema);
  }, [splattedSchema, setSplattedSchema, isRootObject]);

  if (!splattedSchema) {
    return null;
  }

  return (
    <SchemaSplattedSection
      title={title}
      details={details}
      rightContent={<RootObjectListSwitch onToggle={toggleRootObjectList} isRootObject={isRootObject} />}
      className={className}
      style={style}
    >
      <InnerSchemaSplattedEditor
        isRoot
        isRootObject={isRootObject}
        splattedSchema={splattedSchema}
        setSplattedSchema={setSplattedSchema}
        disableImage={disableImage}
        disableAudio={disableAudio}
        disableDocuments={disableDocuments}
        contentRef={contentRef}
      />
    </SchemaSplattedSection>
  );
}
