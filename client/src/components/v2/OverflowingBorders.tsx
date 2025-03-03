type OverflowingBordersProps = {
  margin: number;
  color: string;
};

export function OverflowingVerticalBorders(props: OverflowingBordersProps) {
  const { margin, color } = props;
  return (
    <div
      className={`h-[1px] border-t ${color}`}
      style={{
        width: `calc(100% + ${margin * 2}px)`,
        marginLeft: `-${margin}px`,
        marginRight: `-${margin}px`,
      }}
    />
  );
}

export function OverflowingHorizontalBorders(props: OverflowingBordersProps) {
  const { margin, color } = props;
  return (
    <div
      className={`w-[1px] border-l ${color}`}
      style={{
        height: `calc(100% + ${margin * 2}px)`,
        marginTop: `-${margin}px`,
        marginBottom: `-${margin}px`,
      }}
    />
  );
}
