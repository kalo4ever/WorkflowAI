type GradientBackgroundProps = {
  size?: number;
  className?: string;
};

export function GradientBackground(props: GradientBackgroundProps) {
  const { size = 40, className } = props;
  return (
    <svg
      width={size}
      height={size}
      viewBox='0 0 40 40'
      fill='none'
      xmlns='http://www.w3.org/2000/svg'
      className={className}
    >
      <rect width={size} height={size} rx={size / 2} fill='url(#paint0_radial_15304_98471)' />
      <rect width={size} height={size} rx={size / 2} fill='url(#paint1_angular_15304_98471)' fillOpacity='0.5' />
      <rect width={size} height={size} rx={size / 2} fill='url(#paint2_radial_15304_98471)' fillOpacity='0.4' />
      <rect width={size} height={size} rx={size / 2} fill='url(#paint3_radial_15304_98471)' fillOpacity='0.6' />
      <rect width={size} height={size} rx={size / 2} fill='url(#paint4_radial_15304_98471)' fillOpacity='0.3' />
      <rect width={size} height={size} rx={size / 2} fill='url(#paint5_radial_15304_98471)' fillOpacity='0.1' />
      <rect width={size} height={size} rx={size / 2} fill='url(#paint6_radial_15304_98471)' fillOpacity='0.3' />
      <rect width={size} height={size} rx={size / 2} fill='url(#paint7_radial_15304_98471)' fillOpacity='0.3' />
      <rect width={size} height={size} rx={size / 2} fill='url(#paint8_radial_15304_98471)' fillOpacity='0.2' />
      <rect
        width={size}
        height={size}
        rx={size / 2}
        fill='url(#paint9_radial_15304_98471)'
        fillOpacity='0.7'
        style={{ mixBlendMode: 'hard-light' }}
      />
      <defs>
        <radialGradient
          id='paint0_radial_15304_98471'
          cx='0'
          cy='0'
          r='1'
          gradientUnits='userSpaceOnUse'
          gradientTransform='translate(8.53883 12.9707) rotate(84.7217) scale(25.0434 15.8681)'
        >
          <stop stop-color='#A960EE' />
          <stop offset='1' stop-color='#C788CB' />
        </radialGradient>
        <radialGradient
          id='paint1_angular_15304_98471'
          cx='0'
          cy='0'
          r='1'
          gradientUnits='userSpaceOnUse'
          gradientTransform='translate(8.84274 16.1506) rotate(-88.2154) scale(7.86993 4.3519)'
        >
          <stop offset='0.495182' stop-color='#90E0FF' />
          <stop offset='1' stop-color='#A960EE' stop-opacity='0' />
        </radialGradient>
        <radialGradient
          id='paint2_radial_15304_98471'
          cx='0'
          cy='0'
          r='1'
          gradientUnits='userSpaceOnUse'
          gradientTransform='translate(2.13716 15.7322) rotate(95.0328) scale(24.3617 11.1494)'
        >
          <stop offset='0.411761' stop-color='#FFCB57' />
          <stop offset='0.719902' stop-color='#B778E1' stop-opacity='0' />
        </radialGradient>
        <radialGradient
          id='paint3_radial_15304_98471'
          cx='0'
          cy='0'
          r='1'
          gradientUnits='userSpaceOnUse'
          gradientTransform='translate(9.53632e-07 40) rotate(-42.5497) scale(14.4785 19.1832)'
        >
          <stop offset='0.192069' stop-color='#FF333D' />
          <stop offset='0.545432' stop-color='#B778E0' stop-opacity='0' />
        </radialGradient>
        <radialGradient
          id='paint4_radial_15304_98471'
          cx='0'
          cy='0'
          r='1'
          gradientUnits='userSpaceOnUse'
          gradientTransform='translate(18.3325 7.11297) rotate(-35.1617) scale(9.9957 11.7903)'
        >
          <stop offset='0.317029' stop-color='#FFCB57' />
          <stop offset='1' stop-color='#EE755C' stop-opacity='0' />
        </radialGradient>
        <radialGradient
          id='paint5_radial_15304_98471'
          cx='0'
          cy='0'
          r='1'
          gradientUnits='userSpaceOnUse'
          gradientTransform='translate(7.71534 22.887) rotate(86.8787) scale(16.3841 11.6923)'
        >
          <stop offset='0.507408' stop-color='#90E0FF' />
          <stop offset='1' stop-color='#A960EE' stop-opacity='0' />
        </radialGradient>
        <radialGradient
          id='paint6_radial_15304_98471'
          cx='0'
          cy='0'
          r='1'
          gradientUnits='userSpaceOnUse'
          gradientTransform='translate(3.05993 33.9922) rotate(-127.414) scale(7.17348 6.2469)'
        >
          <stop offset='0.259592' stop-color='#A960EE' />
          <stop offset='1' stop-color='#FF333D' stop-opacity='0' />
        </radialGradient>
        <radialGradient
          id='paint7_radial_15304_98471'
          cx='0'
          cy='0'
          r='1'
          gradientUnits='userSpaceOnUse'
          gradientTransform='translate(2.63318 26.8992) rotate(13.4725) scale(5.49007 8.98693)'
        >
          <stop stop-color='#AFE9FF' />
          <stop offset='0.414475' stop-color='#90E0FF' />
          <stop offset='1' stop-color='#90E0FF' stop-opacity='0' />
        </radialGradient>
        <radialGradient
          id='paint8_radial_15304_98471'
          cx='0'
          cy='0'
          r='1'
          gradientUnits='userSpaceOnUse'
          gradientTransform='translate(22.6656 20) rotate(155.295) scale(15.3943 12.2741)'
        >
          <stop offset='0.447917' stop-color='#FF333D' />
          <stop offset='0.831859' stop-color='#A960EE' stop-opacity='0' />
        </radialGradient>
        <radialGradient
          id='paint9_radial_15304_98471'
          cx='0'
          cy='0'
          r='1'
          gradientUnits='userSpaceOnUse'
          gradientTransform='translate(22.7735 6.44351) rotate(83.4012) scale(26.8726 36.5371)'
        >
          <stop offset='0.166667' stop-color='#EE755C' />
          <stop offset='0.483429' stop-color='#90E0FF' stop-opacity='0' />
        </radialGradient>
      </defs>
    </svg>
  );
}
