export enum CodeLanguage {
  BASH = 'Bash',
  TYPESCRIPT = 'TypeScript',
  PYTHON = 'Python',
  REST = 'Rest',
}

export function displayName(language: CodeLanguage) {
  switch (language) {
    case CodeLanguage.BASH:
      return 'Bash';
    case CodeLanguage.TYPESCRIPT:
      return 'TypeScript';
    case CodeLanguage.PYTHON:
      return 'Python';
    case CodeLanguage.REST:
      return 'RESTful API';
  }
}

export enum InstallInstruction {
  SDK = 'sdk',
  INSTALL = 'install',
  RUN = 'run',
}

export type InstallationSnippet = {
  [key in InstallInstruction]: {
    language: CodeLanguage;
    code: string;
  };
};
