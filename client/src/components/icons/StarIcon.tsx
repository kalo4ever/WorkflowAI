type StarIconProps = {
  size?: number;
  className?: string;
  fill?: string;
};

export function StarIcon(props: StarIconProps) {
  const { size = 16, className, fill } = props;
  return (
    <svg
      xmlns='http://www.w3.org/2000/svg'
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      fill='none'
      className={className}
    >
      <path
        d='M9.88074 5.40659L9.99707 5.64231L10.2572 5.68011L13.6585 6.17434C13.9865 6.22201 14.1175 6.6252 13.8801 6.85662L11.419 9.25566L11.2307 9.43914L11.2752 9.69823L11.8562 13.0857C11.9122 13.4125 11.5692 13.6617 11.2758 13.5074L8.23363 11.908L8.00096 11.7857L7.76829 11.908L4.72612 13.5074C4.43267 13.6617 4.0897 13.4125 4.14574 13.0857L4.72674 9.69823L4.77118 9.43914L4.58294 9.25566L2.12178 6.85662C1.88437 6.6252 2.01538 6.22201 2.34346 6.17434L5.74471 5.68011L6.00485 5.64231L6.12118 5.40659L7.64226 2.32454C7.78899 2.02724 8.21293 2.02724 8.35965 2.32454L9.88074 5.40659Z'
        fill={fill}
        stroke='currentColor'
      />
    </svg>
  );
}
