import { API_URL } from '../constants';

export function getAPIEnvironment(): 'local' | 'development' | 'production' {
  switch (API_URL) {
    case 'http://localhost:8000':
      return 'local';
    case 'https://api.workflowai.dev':
      return 'development';
    default:
      return 'production';
  }
}
