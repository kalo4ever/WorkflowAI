import { act, renderHook } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import * as toaster from '@/components/ui/Sonner';
import { useCopy, useCopyCurrentUrl } from './useCopy';

describe('useCopy', () => {
  beforeEach(() => {
    // This is used to stub the clipboard API
    userEvent.setup();
    jest.spyOn(toaster, 'displaySuccessToaster');
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('copies text to clipboard', async () => {
    const { result } = renderHook(() => useCopy());
    let clipboardText: string = '';
    await act(async () => {
      result.current('test text');
      clipboardText = await navigator.clipboard.readText();
    });
    expect(clipboardText).toEqual('test text');
    expect(toaster.displaySuccessToaster).toHaveBeenCalledWith(
      'Copied to clipboard'
    );
  });

  it('overrides the toaster message', async () => {
    const { result } = renderHook(() => useCopy());
    let clipboardText: string = '';
    await act(async () => {
      result.current('test text', {
        successMessage: 'Custom message',
      });
      clipboardText = await navigator.clipboard.readText();
    });
    expect(clipboardText).toEqual('test text');
    expect(toaster.displaySuccessToaster).toHaveBeenCalledWith(
      'Custom message'
    );
  });
});

describe('useCopyCurrentUrl', () => {
  beforeEach(() => {
    userEvent.setup();
    jest.spyOn(toaster, 'displaySuccessToaster');
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('copies the current URL to the clipboard', async () => {
    const { result } = renderHook(() => useCopyCurrentUrl());
    let clipboardText: string = '';
    await act(async () => {
      result.current();
      clipboardText = await navigator.clipboard.readText();
    });
    // I am worried that this expectation is brittle since we don't explicitly
    // set the location.href in the test.
    expect(clipboardText).toEqual('http://localhost/');
    expect(toaster.displaySuccessToaster).toHaveBeenCalledWith(
      'Page link copied to clipboard'
    );
  });
});
