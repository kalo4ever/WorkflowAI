import { render } from '@testing-library/react';
import { BoolValueViewer } from './BoolValueViewer';

describe('BoolValueViewer', () => {
  it.each([
    { value: true, expected: 'true' },
    { value: false, expected: 'false' },
    { value: null, expected: 'Empty' },
  ])('handles $value', ({ value, expected }) => {
    const { getByTestId } = render(
      <BoolValueViewer schema={{ type: 'boolean' }} value={value} defs={{}} keyPath={''} />
    );
    expect(getByTestId('viewer-readonly-value').textContent).toEqual(expected);
  });
});
