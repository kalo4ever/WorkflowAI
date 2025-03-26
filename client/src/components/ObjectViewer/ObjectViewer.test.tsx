import { composeStories } from '@storybook/react';
import { render } from '@testing-library/react';
import { ObjectViewer } from './ObjectViewer';
import * as stories from './ObjectViewer.stories';

const storiesComponents = composeStories(stories);

describe('ObjectViewer', () => {
  it('renders stories', () => {
    for (const Story of Object.values(storiesComponents)) {
      render(<Story />);
    }
  });

  it('renders sub viewers', async () => {
    const { findAllByTestId } = render(
      <ObjectViewer
        schema={{
          type: 'object',
          properties: {
            name: { type: 'string' },
            age: { type: 'integer' },
            isSuperHero: { type: 'boolean' },
          },
          required: ['name', 'age', 'isSuperHero'],
        }}
        value={{
          name: 'Superman',
          age: 30,
          isSuperHero: true,
        }}
        defs={{}}
        keyPath={''}
      />
    );

    const result = await findAllByTestId('viewer-readonly-value');
    expect(result.length).toEqual(3);
    expect(result[0].textContent).toEqual('Superman');
    expect(result[1].textContent).toEqual('30');
    expect(result[2].textContent).toEqual('true');
  });

  it('avoids infinite recursion when using defs', async () => {
    const { findAllByTestId } = render(
      <ObjectViewer
        schema={{
          properties: {
            name: { type: 'string' },
            createdAt: { allOf: [{ $ref: '#/$defs/DatetimeLocal' }] },
          },
          title: 'DemoAllFieldsTaskInput',
          type: 'object',
        }}
        value={{
          name: 'Object test',
          createdAt: {
            date: '2023-03-01',
            timezone: 'Europe/Paris',
          },
        }}
        defs={{
          DatetimeLocal: {
            description: 'This class represents a local datetime, with a datetime and a timezone.',
            properties: {
              date: {
                examples: ['2023-03-01'],
                format: 'date',
                title: 'Date',
                type: 'string',
              },
              timezone: {
                examples: ['Europe/Paris', 'America/New_York'],
                format: 'timezone',
                type: 'string',
              },
            },
            required: ['date', 'timezone'],
            type: 'object',
          },
        }}
        keyPath={''}
      />
    );

    const result = await findAllByTestId('viewer-readonly-value');
    expect(result.length).toEqual(3);
    expect(result[0].textContent).toEqual('Object test');
    expect(result[1].textContent).toEqual('2023-03-01');
    expect(result[2].textContent).toEqual('Europe/Paris');
  });
});
