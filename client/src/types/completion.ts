import { Span } from './span';

export interface Completion extends Span {
  id: string;
  model: string;
  temperature: number;
  request: Record<string, unknown>;
  response: Record<string, unknown>;
  used_prompt_tokens: number;
  used_completion_tokens: number;
  external_id: string;
}
