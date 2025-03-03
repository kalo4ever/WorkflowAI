export interface RunnerMetadata {
  name: string;
  version: string;
  tags: string[];
  options: {
    model: string;
    temperature: number;
    provider: string;
  };
}
