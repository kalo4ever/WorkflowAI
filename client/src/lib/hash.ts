import * as crypto from 'crypto';

export function hashFile(data: string) {
  return crypto.createHash('sha256').update(data).digest('hex');
}
