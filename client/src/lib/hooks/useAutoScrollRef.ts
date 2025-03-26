import { useEffect } from 'react';
import { useRef } from 'react';

export function useAutoScrollRef(props: { isSelected: boolean; dropdownOpen: boolean | undefined }) {
  const { isSelected, dropdownOpen } = props;

  const selectedRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (selectedRef.current && !!dropdownOpen) {
      selectedRef.current.scrollIntoView({
        block: 'center',
      });
    }
  }, [dropdownOpen]);

  return isSelected ? selectedRef : undefined;
}
