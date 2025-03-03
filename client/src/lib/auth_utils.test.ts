import { getTenantSlug } from './auth_utils';
import { HARDCODED_TENANT } from './constants';

describe('getTenantSlug', () => {
  it('should return the organization slug if it exists', () => {
    const organization = { slug: 'test-org' };
    const user = null;
    const result = getTenantSlug(organization, user);
    expect(result).toBe('test-org');
  });

  it('should return HARDCODED_TENANT when no organization but HARDCODED_TENANT exists', () => {
    const organization = null;
    const user = null;
    const result = getTenantSlug(organization, user);
    expect(result).toBe(HARDCODED_TENANT);
  });

  it('should return user username when no organization exists but user has username', () => {
    const organization = null;
    const user = { id: '1', username: 'testuser', email: 'test@example.com' };
    const result = getTenantSlug(organization, user);
    expect(result).toBe('@testuser');
  });

  it('should return slugified email when no organization or username exists', () => {
    const organization = null;
    const user = { id: '1', email: 'Test.User@example.com' };
    const result = getTenantSlug(organization, user);
    expect(result).toBe('@testuserexamplecom');
  });

  it('should return undefined when no organization, tenant, or user exists', () => {
    const organization = null;
    const user = null;
    const result = getTenantSlug(organization, user);
    expect(result).toBe(undefined);
  });

  it('should return undefined when user has no username or email', () => {
    const organization = null;
    const user = { id: '1' };
    const result = getTenantSlug(organization, user);
    expect(result).toBe(undefined);
  });
});
