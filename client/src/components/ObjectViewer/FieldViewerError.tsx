type FieldViewerErrorProps = {
  error: string | null | undefined;
};

export function FieldViewerError(props: FieldViewerErrorProps) {
  const { error } = props;
  if (!error) {
    return null;
  }
  return (
    <div className='p-1 w-fit'>
      <div className='px-3 py-2 rounded-lg bg-red-100 text-red-600 text-sm font-normal'>{error}</div>
    </div>
  );
}
