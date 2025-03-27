import { cx } from 'class-variance-authority';
import { SchemaEditorField } from '@/lib/schemaEditorUtils';
import { DescriptionExampleSchemaEditor } from './DescriptionExampleSchemaEditor';

type SectionWrapperProps = {
  title: string;
  whiteBackground?: boolean;
  children: React.ReactNode;
};

function SectionWrapper(props: SectionWrapperProps) {
  const { title, whiteBackground, children } = props;
  return (
    <div className={cx('flex-1 flex flex-col rounded-2xl', whiteBackground && 'bg-white shadow-floating')}>
      <div className='text-sm text-slate-500 text-medium px-4 py-3 border-b'>{title}</div>
      <div className='flex-1 px-4 py-3 overflow-auto'>{children}</div>
    </div>
  );
}

type DescriptionExampleEditorProps = {
  inputSplattedSchema: SchemaEditorField | undefined;
  setInputSplattedSchema: (splattedSchema: SchemaEditorField) => void;
  outputSplattedSchema: SchemaEditorField | undefined;
  setOutputSplattedSchema: (splattedSchema: SchemaEditorField) => void;
};

export function DescriptionExampleEditor(props: DescriptionExampleEditorProps) {
  const { inputSplattedSchema, setInputSplattedSchema, outputSplattedSchema, setOutputSplattedSchema } = props;

  if (!inputSplattedSchema || !outputSplattedSchema) {
    return null;
  }

  return (
    <div className='h-full w-full flex flex-col bg-slate-50 overflow-hidden'>
      <div className='flex-1 flex gap-4 p-2 overflow-hidden'>
        <SectionWrapper title='Input'>
          <DescriptionExampleSchemaEditor
            splattedSchema={inputSplattedSchema}
            setSplattedSchema={setInputSplattedSchema}
          />
        </SectionWrapper>
        <SectionWrapper title='Output' whiteBackground>
          <DescriptionExampleSchemaEditor
            splattedSchema={outputSplattedSchema}
            setSplattedSchema={setOutputSplattedSchema}
            showExamples
          />
        </SectionWrapper>
      </div>
    </div>
  );
}
