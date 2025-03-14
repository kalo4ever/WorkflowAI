import { extractTextFromContent } from './utils';

describe('extractTextFromContent', () => {
  it('should return the text from a string', () => {
    const text = 'Hello, world!';
    const result = extractTextFromContent(text);
    expect(result.text).toBe('Hello, world!');
  });

  it('should truncate data urls', () => {
    const data = { url: 'data:image/jpeg;base64,blo=' };
    const result = extractTextFromContent(data);
    expect(result.text).toContain('data:image/jpeg;base64,...truncated');
  });
});
