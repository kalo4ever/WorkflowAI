import type { Config } from 'jest';

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.webp$': '<rootDir>/src/tests/mocks/imageFileMock.ts',
  },
  transform: {
    '^.+\\.(ts|tsx)$': [
      'ts-jest',
      {
        tsconfig: `tsconfig.jest.json`,
      },
    ],
  },
  setupFiles: ['<rootDir>/src/tests/mocks/resizeObserverMock.ts'],
};

export default config;
