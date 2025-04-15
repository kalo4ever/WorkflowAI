import { splitPreview } from './PreviewBox';

describe('splitPreview', () => {
  it('should handle empty string', () => {
    const result = splitPreview('', () => '');
    expect(result).toEqual([]);
  });

  it('should handle string without any markers', () => {
    const result = splitPreview('plain text', () => '');
    expect(result).toEqual(['plain text']);
  });

  it('should handle single marker', () => {
    const result = splitPreview('before [[img:https://example.com/image.jpg]] after', (prefix, url) => {
      expect(prefix).toBe('img');
      expect(url).toBe('https://example.com/image.jpg');
      return 'IMAGE';
    });
    expect(result).toEqual(['before ', 'IMAGE', ' after']);
  });

  it('should handle multiple markers', () => {
    const result = splitPreview(
      'start [[img:https://example.com/1.jpg]] middle [[audio:https://example.com/sound.mp3]] end',
      (prefix, url) => {
        if (prefix === 'img') {
          expect(url).toBe('https://example.com/1.jpg');
          return 'IMAGE';
        } else {
          expect(prefix).toBe('audio');
          expect(url).toBe('https://example.com/sound.mp3');
          return 'AUDIO';
        }
      }
    );
    expect(result).toEqual(['start ', 'IMAGE', ' middle ', 'AUDIO', ' end']);
  });

  it('should handle markers at start and end', () => {
    const result = splitPreview(
      '[[img:https://example.com/start.jpg]] middle [[img:https://example.com/end.jpg]]',
      (prefix) => {
        expect(prefix).toBe('img');
        return 'IMAGE';
      }
    );
    expect(result).toEqual(['IMAGE', ' middle ', 'IMAGE']);
  });

  it('should handle consecutive markers', () => {
    const result = splitPreview('[[img:https://example.com/1.jpg]][[img:]]', (prefix) => {
      expect(prefix).toBe('img');
      return 'IMAGE';
    });
    expect(result).toEqual(['IMAGE', 'IMAGE']);
  });

  it('should handle markers with special characters in content', () => {
    const result = splitPreview('[[img:https://example.com/image.jpg?param=value&other=param]]', (prefix, url) => {
      expect(prefix).toBe('img');
      expect(url).toBe('https://example.com/image.jpg?param=value&other=param');
      return 'IMAGE';
    });
    expect(result).toEqual(['IMAGE']);
  });
});
