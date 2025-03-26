export function ReviewsHeader() {
  return (
    <div className='px-2 py-2.5 flex items-center gap-4 w-full border-b border-gray-100 font-lato text-gray-900 text-[13px] font-medium'>
      <div className='flex items-center w-[25%]'>Input</div>
      <div className='flex items-center w-[25%]'>Accurate Outputs</div>
      <div className='flex items-center w-[25%]'>Inaccurate Outputs</div>
      <div className='flex items-center w-[25%]'>Input Specific Instructions</div>
    </div>
  );
}
