type ManageCardsTooltipContentProps = {
  text: string | undefined;
  showDismiss: boolean;
  onDismiss: (event: React.MouseEvent) => void;
};

export function ManageCardsTooltipContent(
  props: ManageCardsTooltipContentProps
) {
  const { text, showDismiss, onDismiss } = props;

  if (!text) {
    return null;
  }

  return (
    <div className='flex flex-col gap-2'>
      <div className='whitespace-pre-line'>{text}</div>
      {showDismiss && (
        <div className='flex justify-start'>
          <div
            className='flex items-center justify-center font-semibold bg-gray-700 text-white hover:bg-gray-600 rounded-[2px] text-[13px] h-9 px-4 py-2'
            onClick={onDismiss}
          >
            Dismiss
          </div>
        </div>
      )}
    </div>
  );
}
