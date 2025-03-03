type ImagePlaceholderIconProps = {
  className?: string;
};

export function ImagePlaceholderIcon(props: ImagePlaceholderIconProps) {
  const { className } = props;

  return (
    <svg
      width='17'
      height='16'
      viewBox='0 0 17 16'
      fill='none'
      xmlns='http://www.w3.org/2000/svg'
      className={className}
    >
      <g id='Image Placeholder'>
        <g clipPath='url(#clip0_7873_44667)'>
          <path
            d='M0.5 4C0.5 1.79086 2.29086 0 4.5 0H12.5C14.7091 0 16.5 1.79086 16.5 4V12C16.5 14.2091 14.7091 16 12.5 16H4.5C2.29086 16 0.5 14.2091 0.5 12V4Z'
            fill='#E2E8F0'
          />
          <path
            id='Vector 469'
            d='M4.9374 11.1692L0.500488 8V16H16.5005V5.6L14.3902 4.54488C13.7464 4.22298 12.9669 4.3706 12.4854 4.90562L7.05665 10.9376C6.51204 11.5427 5.59987 11.6424 4.9374 11.1692Z'
            fill='#475569'
          />
          <circle id='Ellipse 11' cx='5.3002' cy='5.6' r='1.6' fill='#475569' />
        </g>
      </g>
      <defs>
        <clipPath id='clip0_7873_44667'>
          <path
            d='M0.5 4C0.5 1.79086 2.29086 0 4.5 0H12.5C14.7091 0 16.5 1.79086 16.5 4V12C16.5 14.2091 14.7091 16 12.5 16H4.5C2.29086 16 0.5 14.2091 0.5 12V4Z'
            fill='white'
          />
        </clipPath>
      </defs>
    </svg>
  );
}
