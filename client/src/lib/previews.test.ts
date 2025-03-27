import { GeneralizedTaskInput } from '@/types';
import { computePreview } from './previews';

const INPUT_PREVIEWS: { input: GeneralizedTaskInput; preview: string }[] = [
  {
    input: {
      actual: {
        category: 'A',
      },
      input: {
        value: 'flour',
      },
    },
    preview: `actual: {category: "A"}, input: {value: "flour"}`,
  },
  {
    input: {
      score: 0,
      reason: "The value 'flour' is a vegetarian ingredient, so the category should be 'B'.",
    },
    preview: `score: 0, reason: \"The value 'flour' is a vegetarian ingredient, so the category should be 'B'.\"`,
  },
  {
    input: {
      cities: ['Madrid', 'Bangkok', 'Istanbul'],
    },
    preview: `cities: ["Madrid", "Bangkok", "Istanbul"]`,
  },
  {
    input: {
      city_metadata: [
        {
          city: 'Madrid',
          number_of_habitants: 3223000,
          language: 'Spanish',
          main_religion: 'Christianity',
          altitude: 667,
          country: 'Spain',
          currency: 'EUR',
        },
        {
          city: 'Bangkok',
          number_of_habitants: 10539000,
          language: 'Thai',
          main_religion: 'Buddhism',
          altitude: 1.5,
          country: 'Thailand',
          currency: 'THB',
        },
        {
          city: 'Istanbul',
          number_of_habitants: 15460000,
          language: 'Turkish',
          main_religion: 'Islam',
          altitude: 40,
          country: 'Turkey',
          currency: 'TRY',
        },
      ],
    },
    preview: `city_metadata: [{city: \"Madrid\", number_of_habitants: 3223000, language: \"Spanish\", main_religion: \"Christianity\", altitude: 667, country: \"Spain\", currency: \"EUR\"}, {city: \"Bangkok\", number_of_habita`,
  },
];

describe('computePreview', () => {
  it('returns a preview of the input', () => {
    for (const { input, preview } of INPUT_PREVIEWS) {
      expect(computePreview(input)).toBe(preview);
    }
  });

  it('returns a preview of the input with a custom max length', () => {
    for (const { input, preview } of INPUT_PREVIEWS) {
      expect(computePreview(input, 10)).toBe(preview.slice(0, 10));
    }
  });

  it('returns "-" for undefined input', () => {
    expect(computePreview(undefined)).toBe('-');
  });
});
