import type { KnipConfig } from 'knip';

const config: KnipConfig = {
  next: {
    entry: [
      'next.config.{js,ts,cjs,mjs}',
      'openapi-ts.config.cjs',
      'src/middleware.{js,ts}',
      'src/app/global-error.tsx',
      'src/app/**/{error,layout,loading,not-found,page,route,template,default}.{js,jsx,ts,tsx}',
      'src/app/{manifest,sitemap,robots}.{js,ts}',
      '!src/types/workflowAI/*',
      '!**/__mocks__/**/*',
    ],
  },
  storybook: {
    config: ['.storybook/{main,test-runner}.{js,ts}'],
    entry: ['.storybook/{manager,preview}.{js,jsx,ts,tsx}', '**/*.@(mdx|stories.@(mdx|js|jsx|mjs|ts|tsx))'],
    project: ['.storybook/**/*.{js,jsx,ts,tsx}'],
  },
};

export default config;
