import Image from 'next/image';
import React, { useCallback, useState } from 'react';

interface ImageWithPlaceholderProps {
  imageUrl: string;
  placeholderUrl: string;
  className?: string;
  unoptimized?: boolean;
  taskName?: string;
}

export function ImageWithPlaceholder(props: ImageWithPlaceholderProps) {
  const { imageUrl, placeholderUrl, className, unoptimized } = props;

  const [wrappedImageUrl, setWrappedImageUrl] = useState(imageUrl);

  const onError = useCallback(() => {
    setWrappedImageUrl(placeholderUrl);
  }, [placeholderUrl]);

  return (
    <div>
      <Image
        src={wrappedImageUrl}
        alt='Image'
        layout='fill'
        objectFit='cover'
        className={className}
        onError={onError}
        unoptimized={unoptimized}
        placeholder='blur'
        blurDataURL={placeholderUrl}
      />
    </div>
  );
}
