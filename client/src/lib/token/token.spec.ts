/**
 * @jest-environment node
 */
import { TenantID } from '@/types/aliases';
import {
  build_api_jwt,
  build_api_jwt_for_tenant,
  export_public_key,
  parse_sign_key,
} from './token';

const raw_key =
  'LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tCk1JR0hBZ0VBTUJNR0J5cUdTTTQ5QWdFR0NDcUdTTTQ5QXdFSEJHMHdhd0lCQVFRZ3l0NC91U0VKQ09OUi9RZTIKWUQxZERMUTliNWhxSUhTb3BTTzZucjhnUU5paFJBTkNBQVRxY2RNa0tQakMzWFNFM21kMjlJVWxDekNsQ01iegpaRU5PdXpzUnVIdTNoVUg0YjF2TEw5N2d0UFo0bFdQdkFYcG8vcDJadHg3blZFa3k2aXJSVk5zNQotLS0tLUVORCBQUklWQVRFIEtFWS0tLS0tCg==';

describe('parse_sign_key', () => {
  it('parses a key', async () => {
    // Check that we don't throw
    await parse_sign_key(raw_key);
  });
});

describe('build_api_jwt', () => {
  it('builds a jwt', async () => {
    const sign_key = await parse_sign_key(raw_key);
    const jwt = await build_api_jwt(
      { tenant: 'test1' as TenantID, sub: 'test2' },
      '60d',
      sign_key
    );

    const splits = jwt.split('.');
    expect(splits).toHaveLength(3);

    const decoded = Buffer.from(splits[1], 'base64').toString('utf-8');
    const payload = JSON.parse(decoded);

    expect(payload).toMatchObject({
      tenant: 'test1',
      sub: 'test2',
    });
  });
});

describe('export_public_key', () => {
  it('exports a public key', async () => {
    const sign_key = await parse_sign_key(raw_key);
    const jwk = await export_public_key(sign_key);
    // Check that "d" is not in there
    expect(jwk).toEqual({
      kty: 'EC',
      x: '6nHTJCj4wt10hN5ndvSFJQswpQjG82RDTrs7Ebh7t4U',
      y: 'QfhvW8sv3uC09niVY-8Bemj-nZm3HudUSTLqKtFU2zk',
      crv: 'P-256',
    });
  });
});

describe('build_api_jwt_for_tenant', () => {
  it('builds a jwt for an anon user', async () => {
    const sign_key = await parse_sign_key(raw_key);

    const jwt = await build_api_jwt_for_tenant(
      {
        unknownUserId: 'test1',
      },
      '1d',
      sign_key
    );
    const { iat, exp, ...rest } = JSON.parse(
      Buffer.from(jwt.split('.')[1], 'base64').toString('utf-8')
    );
    expect(iat).toBeDefined();
    expect(exp).toEqual(iat + 1 * 24 * 60 * 60);
    expect(rest).toEqual({
      unknownUserId: 'test1',
    });
  });
});
