type CircularProgressProps = {
  value: number;
  warning: boolean;
  backgroundColor?: string;
  foregroundColor?: string;
  warrningColor?: string;
};

export function CircularProgress(props: CircularProgressProps) {
  const { value, warning, backgroundColor = '#F0F4F8', foregroundColor = '#D946EF', warrningColor = '#EF4444' } = props;

  const radius = 18;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (value / 100) * circumference;

  return (
    <svg width='40' height='40' viewBox='0 0 40 40' className='transform -rotate-90 animate-transform'>
      <circle cx='20' cy='20' r={radius} stroke={backgroundColor} strokeWidth='4' fill='transparent' />
      <circle
        cx='20'
        cy='20'
        r={radius}
        stroke={warning ? warrningColor : foregroundColor}
        strokeWidth='4'
        fill='transparent'
        strokeDasharray={`${circumference} ${circumference}`}
        strokeDashoffset={-strokeDashoffset}
        strokeLinecap='round'
      />
    </svg>
  );
}
