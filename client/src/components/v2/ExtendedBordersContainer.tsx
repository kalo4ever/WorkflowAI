import { cn } from '@/lib/utils';

type ExtendedBordersContainerProps = {
  className?: string;
  children?: React.ReactNode;
  margin?: number;
  borderColor?: string;
  readonly borders?: readonly ('left' | 'right' | 'top' | 'bottom')[];
};

const defaultBorders = ['left', 'right', 'top', 'bottom'] as const;

export function ExtendedBordersContainer({
  className,
  children,
  margin = 0,
  borderColor,
  borders = defaultBorders,
}: ExtendedBordersContainerProps) {
  return (
    <div className={cn('relative', className)}>
      {/* Left border */}
      {borders.includes('left') && (
        <div
          className={cn('absolute w-[1px]', borderColor ? `bg-${borderColor}` : 'bg-border')}
          style={{
            left: 0,
            top: `-${margin}px`,
            bottom: `-${margin}px`,
          }}
        />
      )}

      {/* Right border */}
      {borders.includes('right') && (
        <div
          className={cn('absolute w-[1px]', borderColor ? `bg-${borderColor}` : 'bg-border')}
          style={{
            right: 0,
            top: `-${margin}px`,
            bottom: `-${margin}px`,
          }}
        />
      )}

      {/* Top border */}
      {borders.includes('top') && (
        <div
          className={cn('absolute h-[1px]', borderColor ? `bg-${borderColor}` : 'bg-border')}
          style={{
            top: 0,
            left: `-${margin}px`,
            right: `-${margin}px`,
          }}
        />
      )}

      {/* Bottom border */}
      {borders.includes('bottom') && (
        <div
          className={cn('absolute h-[1px]', borderColor ? `bg-${borderColor}` : 'bg-border')}
          style={{
            bottom: 0,
            left: `-${margin}px`,
            right: `-${margin}px`,
          }}
        />
      )}

      {children}
    </div>
  );
}
