/* eslint-disable max-lines */
import { SchemaEditorField } from '@/lib/schemaEditorUtils';
import { JsonSchema } from '@/types';
import { SchemaEditorTextCaseFixture } from './types';

const originalSchema: JsonSchema = {
  type: 'object',
  properties: {
    articles: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: {
            type: 'string',
            description: 'Unique identifier for the article',
            examples: ['123', '456'],
          },
          keywords: {
            type: 'array',
            items: {
              type: 'string',
            },
            description: 'Keywords associated with the article',
            examples: [
              ['finance', 'technology'],
              ['health', 'innovation'],
            ],
          },
          title: {
            type: 'string',
            description: 'Title of the article',
            examples: ['Breaking News in Tech', 'Latest Health Updates'],
          },
          published: {
            type: 'number',
            description: 'Unix timestamp of when the article was published',
            examples: [1609459200, 1612137600],
          },
          summary: {
            type: 'object',
            properties: {
              content: {
                type: 'string',
                description: 'Summary content of the article',
                examples: [
                  'Summary of the article content',
                  'Brief overview of the article',
                ],
              },
            },
            description: 'Summary of the article',
          },
          author: {
            type: 'string',
            description: 'Author of the article',
            examples: ['John Doe', 'Jane Smith'],
          },
          canonicalUrl: {
            type: 'string',
            description: 'Canonical URL of the article',
            examples: [
              'https://example.com/article1',
              'https://example.com/article2',
            ],
          },
          abstract: {
            type: 'object',
            properties: {
              text: {
                type: 'string',
                description: 'Abstract text of the article',
                examples: ['Abstract content', 'Detailed abstract text'],
              },
            },
            description: 'Abstract of the article',
          },
          content: {
            type: 'object',
            properties: {
              content: {
                type: 'string',
                description: 'Main content of the article',
                examples: [
                  'Full content of the article',
                  'Detailed article content',
                ],
              },
            },
            description: 'Content of the article',
          },
          fullContent: {
            type: 'string',
            description: 'Complete content of the article',
            examples: ['Complete article text', 'Full text of the article'],
          },
          businessEvents: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                label: {
                  type: 'string',
                  description: 'Label describing the business event',
                  examples: ['Product Launch', 'Merger Announcement'],
                },
                salienceLevel: {
                  type: 'string',
                  description: 'Importance level of the business event',
                  examples: ['High', 'Medium'],
                },
              },
            },
            description: 'Business events mentioned in the article',
          },
          entities: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                label: {
                  type: 'string',
                  description: 'Label of the entity',
                  examples: ['Google', 'Apple'],
                },
                salienceLevel: {
                  type: 'string',
                  description: 'Importance level of the entity',
                  examples: ['High', 'Low'],
                },
              },
            },
            description: 'Entities mentioned in the article',
          },
          origin: {
            type: 'object',
            properties: {
              title: {
                type: 'string',
                description: 'Title of the origin source',
                examples: ['New York Times', 'TechCrunch'],
              },
            },
            description: 'Origin of the article',
          },
          engagement: {
            type: 'number',
            description: 'Engagement score of the article',
            examples: [150, 200],
          },
          engagementRate: {
            type: 'number',
            description: 'Engagement rate of the article',
            examples: [1.5, 2],
          },
          leoSummary: {
            type: 'object',
            properties: {
              sentences: {
                type: 'array',
                items: {
                  type: 'object',
                  properties: {
                    text: {
                      type: 'string',
                      description: 'Text of the sentence',
                      examples: [
                        'Summary sentence one',
                        'Summary sentence two',
                      ],
                    },
                    score: {
                      type: 'number',
                      description: 'Score of the sentence',
                      examples: [0.8, 0.9],
                    },
                  },
                },
              },
            },
            description: 'LEO-generated summary of the article',
          },
          sanitizedContent: {
            type: 'string',
            description: 'Sanitized content of the article',
            examples: [
              'Sanitized text of the article',
              'Cleaned article content',
            ],
          },
          openAiSummary: {
            type: 'string',
            description: 'OpenAI-generated summary of the article',
            examples: ['OpenAI summary text', 'Generated summary content'],
          },
          sentiment: {
            type: 'string',
            enum: ['positive', 'negative', 'neutral'],
            description: 'Sentiment of the article',
            examples: ['positive', 'negative'],
          },
          thriveCompanies: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                id: {
                  type: 'string',
                  description: 'ID of the company',
                  examples: ['comp123', 'comp456'],
                },
                name: {
                  type: 'string',
                  description: 'Name of the company',
                  examples: ['Thrive Tech', 'Health Innovations'],
                },
                logoUrl: {
                  type: 'string',
                  description: 'URL of the company logo',
                  examples: [
                    'https://example.com/logo1.png',
                    'https://example.com/logo2.png',
                  ],
                },
              },
            },
            description: 'Companies mentioned in the article',
          },
        },
      },
    },
  },
};

const splattedEditorFields: SchemaEditorField = {
  keyName: '',
  type: 'object',
  fields: [
    {
      keyName: 'articles',
      type: 'array',
      arrayType: 'object',
      fields: [
        {
          keyName: 'id',
          type: 'string',
          description: 'Unique identifier for the article',
          examples: ['123', '456'],
        },
        {
          keyName: 'keywords',
          type: 'array',
          arrayType: 'string',
          fields: [
            {
              keyName: 'keywords',
              type: 'string',
            },
          ],
          description: 'Keywords associated with the article',
          examples: [
            ['finance', 'technology'],
            ['health', 'innovation'],
          ],
        },
        {
          keyName: 'title',
          type: 'string',
          description: 'Title of the article',
          examples: ['Breaking News in Tech', 'Latest Health Updates'],
        },
        {
          keyName: 'published',
          type: 'number',
          description: 'Unix timestamp of when the article was published',
          examples: [1609459200, 1612137600],
        },
        {
          keyName: 'summary',
          type: 'object',
          fields: [
            {
              keyName: 'content',
              type: 'string',
              description: 'Summary content of the article',
              examples: [
                'Summary of the article content',
                'Brief overview of the article',
              ],
            },
          ],
          description: 'Summary of the article',
        },
        {
          keyName: 'author',
          type: 'string',
          description: 'Author of the article',
          examples: ['John Doe', 'Jane Smith'],
        },
        {
          keyName: 'canonicalUrl',
          type: 'string',
          description: 'Canonical URL of the article',
          examples: [
            'https://example.com/article1',
            'https://example.com/article2',
          ],
        },
        {
          keyName: 'abstract',
          type: 'object',
          fields: [
            {
              keyName: 'text',
              type: 'string',
              description: 'Abstract text of the article',
              examples: ['Abstract content', 'Detailed abstract text'],
            },
          ],
          description: 'Abstract of the article',
        },
        {
          keyName: 'content',
          type: 'object',
          fields: [
            {
              keyName: 'content',
              type: 'string',
              description: 'Main content of the article',
              examples: [
                'Full content of the article',
                'Detailed article content',
              ],
            },
          ],
          description: 'Content of the article',
        },
        {
          keyName: 'fullContent',
          type: 'string',
          description: 'Complete content of the article',
          examples: ['Complete article text', 'Full text of the article'],
        },
        {
          keyName: 'businessEvents',
          type: 'array',
          arrayType: 'object',
          fields: [
            {
              keyName: 'label',
              type: 'string',
              description: 'Label describing the business event',
              examples: ['Product Launch', 'Merger Announcement'],
            },
            {
              keyName: 'salienceLevel',
              type: 'string',
              description: 'Importance level of the business event',
              examples: ['High', 'Medium'],
            },
          ],
          description: 'Business events mentioned in the article',
        },
        {
          keyName: 'entities',
          type: 'array',
          arrayType: 'object',
          fields: [
            {
              keyName: 'label',
              type: 'string',
              description: 'Label of the entity',
              examples: ['Google', 'Apple'],
            },
            {
              keyName: 'salienceLevel',
              type: 'string',
              description: 'Importance level of the entity',
              examples: ['High', 'Low'],
            },
          ],
          description: 'Entities mentioned in the article',
        },
        {
          keyName: 'origin',
          type: 'object',
          fields: [
            {
              keyName: 'title',
              type: 'string',
              description: 'Title of the origin source',
              examples: ['New York Times', 'TechCrunch'],
            },
          ],
          description: 'Origin of the article',
        },
        {
          keyName: 'engagement',
          type: 'number',
          description: 'Engagement score of the article',
          examples: [150, 200],
        },
        {
          keyName: 'engagementRate',
          type: 'number',
          description: 'Engagement rate of the article',
          examples: [1.5, 2],
        },
        {
          keyName: 'leoSummary',
          type: 'object',
          fields: [
            {
              keyName: 'sentences',
              type: 'array',
              arrayType: 'object',
              fields: [
                {
                  keyName: 'text',
                  type: 'string',
                  description: 'Text of the sentence',
                  examples: ['Summary sentence one', 'Summary sentence two'],
                },
                {
                  keyName: 'score',
                  type: 'number',
                  description: 'Score of the sentence',
                  examples: [0.8, 0.9],
                },
              ],
            },
          ],
          description: 'LEO-generated summary of the article',
        },
        {
          keyName: 'sanitizedContent',
          type: 'string',
          description: 'Sanitized content of the article',
          examples: [
            'Sanitized text of the article',
            'Cleaned article content',
          ],
        },
        {
          keyName: 'openAiSummary',
          type: 'string',
          description: 'OpenAI-generated summary of the article',
          examples: ['OpenAI summary text', 'Generated summary content'],
        },
        {
          keyName: 'sentiment',
          type: 'enum',
          enum: ['positive', 'negative', 'neutral'],
          description: 'Sentiment of the article',
          examples: ['positive', 'negative'],
        },
        {
          keyName: 'thriveCompanies',
          type: 'array',
          arrayType: 'object',
          fields: [
            {
              keyName: 'id',
              type: 'string',
              description: 'ID of the company',
              examples: ['comp123', 'comp456'],
            },
            {
              keyName: 'name',
              type: 'string',
              description: 'Name of the company',
              examples: ['Thrive Tech', 'Health Innovations'],
            },
            {
              keyName: 'logoUrl',
              type: 'string',
              description: 'URL of the company logo',
              examples: [
                'https://example.com/logo1.png',
                'https://example.com/logo2.png',
              ],
            },
          ],
          description: 'Companies mentioned in the article',
        },
      ],
    },
  ],
};

export const productionObjectsSchemaFixture: SchemaEditorTextCaseFixture = {
  originalSchema,
  splattedEditorFields,
  finalSchema: originalSchema,
};
