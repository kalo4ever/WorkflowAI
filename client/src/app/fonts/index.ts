import localFont from 'next/font/local';

export const OpenRunde = localFont({
  src: [
    {
      path: './OpenRunde-1.0.1/OpenRunde-Regular.otf',
      weight: '400',
      style: 'normal',
    },
  ],
  variable: '--font-open-runde',
});

export const Inter = localFont({
  src: [
    {
      path: './Inter/Inter-VariableFont.ttf',
      weight: 'variable',
      style: 'normal',
    },
  ],
  variable: '--font-inter',
});

export const Lato = localFont({
  src: [
    {
      path: './Lato/Lato-Thin.ttf',
      weight: '100',
      style: 'normal',
    },
    {
      path: './Lato/Lato-ExtraLight.ttf',
      weight: '200',
      style: 'normal',
    },
    {
      path: './Lato/Lato-Light.ttf',
      weight: '300',
      style: 'normal',
    },
    {
      path: './Lato/Lato-Regular.ttf',
      weight: '400',
      style: 'normal',
    },
    {
      path: './Lato/Lato-Medium.ttf',
      weight: '500',
      style: 'normal',
    },
    {
      path: './Lato/Lato-SemiBold.ttf',
      weight: '600',
      style: 'normal',
    },
    {
      path: './Lato/Lato-Bold.ttf',
      weight: '700',
      style: 'normal',
    },
    {
      path: './Lato/Lato-ExtraBold.ttf',
      weight: '800',
      style: 'normal',
    },
    {
      path: './Lato/Lato-Black.ttf',
      weight: '900',
      style: 'normal',
    },
  ],
  variable: '--font-lato',
});
