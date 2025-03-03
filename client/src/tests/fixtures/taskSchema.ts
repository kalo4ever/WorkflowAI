/* eslint-disable max-lines */
import { JsonSchema, TaskRun, TaskSchemaResponseWithSchema } from '@/types';
import { SerializableTaskIOWithSchema } from '@/types/task';

export const taskSchemaFixture: {
  simpleSchema: JsonSchema;
  taskSchema: TaskSchemaResponseWithSchema;
  taskRun: TaskRun;
  taskSchemaImage: SerializableTaskIOWithSchema;
  taskSchemaImageArray: SerializableTaskIOWithSchema;
  taskInputImage: Record<string, unknown>;
} = {
  simpleSchema: {
    $defs: {
      CalendarEventCategory: {
        enum: [
          'UNSPECIFIED',
          'IN_PERSON_MEETING',
          'REMOTE_MEETING',
          'FLIGHT',
          'TO_DO',
          'BIRTHDAY',
        ],
        title: 'CalendarEventCategory',
        type: 'string',
      },
      MeetingProvider: {
        enum: ['ZOOM', 'GOOGLE_MEET', 'MICROSOFT_TEAMS', 'SKYPE', 'OTHER'],
        title: 'MeetingProvider',
        type: 'string',
      },
    },
    description:
      'The expected output of the EmailToCalendarProcessor.\nEach attribute corresponds to a question asked to the processor.\n\nThis class will be dynamically injected in the prompt as a "schema" for the LLM to enforce.',
    properties: {
      is_email_thread_about_an_event: {
        title: 'Is Email Thread About An Event',
        type: 'boolean',
      },
      is_event_confirmed: {
        anyOf: [{ type: 'boolean' }, { type: 'null' }],
        title: 'Is Event Confirmed',
      },
      event_category: {
        anyOf: [{ $ref: '#/$defs/CalendarEventCategory' }, { type: 'null' }],
      },
      is_event_all_day: { title: 'Is Event All Day', type: 'boolean' },
      is_event_start_datetime_defined: {
        anyOf: [{ type: 'boolean' }, { type: 'null' }],
        title: 'Is Event Start Datetime Defined',
      },
      event_start_datetime: {
        anyOf: [{ format: 'date-time', type: 'string' }, { type: 'null' }],
        title: 'Event Start Datetime',
      },
      event_start_date: {
        anyOf: [{ format: 'date', type: 'string' }, { type: 'null' }],
        title: 'Event Start Date',
      },
      is_event_end_datetime_defined: {
        anyOf: [{ type: 'boolean' }, { type: 'null' }],
        title: 'Is Event End Datetime Defined',
      },
      event_end_datetime: {
        anyOf: [{ format: 'date-time', type: 'string' }, { type: 'null' }],
        title: 'Event End Datetime',
      },
      event_end_date: {
        anyOf: [{ format: 'date', type: 'string' }, { type: 'null' }],
        title: 'Event End Date',
      },
      event_title: {
        anyOf: [{ type: 'string' }, { type: 'null' }],
        title: 'Event Title',
      },
      remote_meeting_provider: {
        anyOf: [{ $ref: '#/$defs/MeetingProvider' }, { type: 'null' }],
      },
      event_location_details: {
        anyOf: [{ type: 'string' }, { type: 'null' }],
        title: 'Event Location Details',
      },
      event_participants_emails_addresses: {
        anyOf: [{ items: { type: 'string' }, type: 'array' }, { type: 'null' }],
        title: 'Event Participants Emails Addresses',
      },
    },
    required: [
      'is_email_thread_about_an_event',
      'is_event_confirmed',
      'event_category',
      'is_event_all_day',
      'is_event_start_datetime_defined',
      'event_start_datetime',
      'event_start_date',
      'is_event_end_datetime_defined',
      'event_end_datetime',
      'event_end_date',
      'event_title',
      'remote_meeting_provider',
      'event_location_details',
      'event_participants_emails_addresses',
    ],
    title: 'EmailToCalendarOutput',
    type: 'object',
  },
  taskSchema: {
    is_hidden: false,
    task_id: 'article-theme-synthesis',
    schema_id: 1,
    name: 'Article Theme Synthesis',
    input_schema: {
      version: '7360b171747c256f77dd975fdbbd2183',
      json_schema: {
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
                  description:
                    'Unix timestamp of when the article was published',
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
                  format: 'uri',
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
                  examples: [
                    'Complete article text',
                    'Full text of the article',
                  ],
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
                  examples: [
                    'OpenAI summary text',
                    'Generated summary content',
                  ],
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
                        format: 'uri',
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
              required: [
                'id',
                'title',
                'published',
                'canonicalUrl',
                'businessEvents',
                'entities',
                'origin',
                'engagement',
                'engagementRate',
              ],
            },
          },
        },
        required: ['articles'],
        $defs: {
          DatetimeLocal: {
            description:
              'This class represents a local datetime, with a datetime and a timezone.',
            properties: {
              date: {
                description: 'The date of the local datetime.',
                examples: ['2023-03-01'],
                format: 'date',
                title: 'Date',
                type: 'string',
              },
              local_time: {
                description:
                  'The time of the local datetime without timezone info.',
                examples: ['12:00:00', '22:00:00'],
                format: 'time',
                title: 'Local Time',
                type: 'string',
              },
              timezone: {
                description: 'The timezone of the local time.',
                examples: ['Europe/Paris', 'America/New_York'],
                format: 'timezone',
                title: 'Timezone',
                type: 'string',
              },
            },
            required: ['date', 'local_time', 'timezone'],
            title: 'DatetimeLocal',
            type: 'object',
          },
        },
      },
    },
    output_schema: {
      version: '274102a19cc73ddab050de40d58248ec',
      json_schema: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            companyName: {
              type: 'string',
              description: 'Name of the company',
              examples: ['Thrive Tech', 'Health Innovations'],
            },
            companyId: {
              type: 'string',
              description: 'Unique identifier for the company',
              examples: ['comp123', 'comp456'],
            },
            logoUrl: {
              type: 'string',
              format: 'uri',
              description: 'URL of the company logo',
              examples: [
                'https://example.com/logo1.png',
                'https://example.com/logo2.png',
              ],
            },
            articleCollections: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  topic: {
                    type: 'string',
                    description: 'Topic of the article collection',
                    examples: ['Technology', 'Healthcare'],
                  },
                  summary: {
                    type: 'string',
                    description:
                      'Summary encompassing the general theme of the articles',
                    examples: [
                      'Summary of tech advancements',
                      'Overview of health sector trends',
                    ],
                  },
                  articles: {
                    type: 'array',
                    items: {
                      type: 'object',
                      properties: {
                        title: {
                          type: 'string',
                          description: 'Title of the article',
                          examples: [
                            'Breaking News in Tech',
                            'Latest Health Updates',
                          ],
                        },
                        url: {
                          type: 'string',
                          format: 'uri',
                          description: 'URL of the article',
                          examples: [
                            'https://example.com/article1',
                            'https://example.com/article2',
                          ],
                        },
                        author: {
                          type: 'string',
                          description: 'Author of the article',
                          examples: ['John Doe', 'Jane Smith'],
                        },
                        source: {
                          type: 'string',
                          description: 'Source of the article',
                          examples: ['New York Times', 'TechCrunch'],
                        },
                        published: {
                          type: 'number',
                          description:
                            'Unix timestamp of when the article was published',
                          examples: [1609459200, 1612137600],
                        },
                        sentiment: {
                          type: 'string',
                          enum: ['positive', 'negative', 'neutral'],
                          description: 'Sentiment of the article',
                          examples: ['positive', 'negative'],
                        },
                        businessEvents: {
                          type: 'array',
                          items: {
                            type: 'object',
                            properties: {
                              label: {
                                type: 'string',
                                description:
                                  'Label describing the business event',
                                examples: [
                                  'Product Launch',
                                  'Merger Announcement',
                                ],
                              },
                              salienceLevel: {
                                type: 'string',
                                description:
                                  'Importance level of the business event',
                                examples: ['High', 'Medium'],
                              },
                            },
                          },
                          description:
                            'Business events mentioned in the article',
                        },
                      },
                      required: ['title', 'url', 'published', 'businessEvents'],
                    },
                  },
                },
                required: ['topic', 'summary', 'articles'],
              },
            },
          },
          required: ['companyName', 'companyId', 'articleCollections'],
        },
        $defs: {
          DatetimeLocal: {
            description:
              'This class represents a local datetime, with a datetime and a timezone.',
            properties: {
              date: {
                description: 'The date of the local datetime.',
                examples: ['2023-03-01'],
                format: 'date',
                title: 'Date',
                type: 'string',
              },
              local_time: {
                description:
                  'The time of the local datetime without timezone info.',
                examples: ['12:00:00', '22:00:00'],
                format: 'time',
                title: 'Local Time',
                type: 'string',
              },
              timezone: {
                description: 'The timezone of the local time.',
                examples: ['Europe/Paris', 'America/New_York'],
                format: 'timezone',
                title: 'Timezone',
                type: 'string',
              },
            },
            required: ['date', 'local_time', 'timezone'],
            title: 'DatetimeLocal',
            type: 'object',
          },
        },
      },
    },
  },
  taskRun: {
    id: 'cd3c4ff6-9e6a-463f-866a-f8ace993771f',
    task_id: 'article-theme-synthesis',
    task_schema_id: 1,
    task_input: {
      articles: [
        {
          id: 'art789',
          title: 'Innovations in Renewable Energy',
          published: 1627737600,
          canonicalUrl: 'https://greenlight.com/renewable-energy',
          businessEvents: [
            {
              label: 'Green Energy Tech',
              salienceLevel: 'High',
            },
          ],
          entities: [
            {
              label: 'Tesla',
              salienceLevel: 'High',
            },
            {
              label: 'SolarCity',
              salienceLevel: 'Medium',
            },
          ],
          origin: {
            title: 'GreenTech Magazine',
          },
          engagement: 345,
          engagementRate: 3.4,
          sentiment: 'positive',
          keywords: ['sustainability', 'renewable energy', 'technology'],
          author: 'Emily Rose',
          summary: {
            content:
              'The article discusses the latest advancements and the rising investment in the field of renewable energy.',
          },
          abstract: {
            text: 'This article highlights significant innovations and investments in renewable energy, outlining potential impacts on the industry.',
          },
          content: {
            content:
              'As the world leaps towards more sustainable solutions, new technologies in solar and wind energy lead the way. The article delves into how these technologies play a key role in shaping the future.',
          },
          fullContent:
            'With global emphasis on sustainability, renewable energy sources like solar and wind are witnessing revolutionary developments. The text explores various projects and their implications for future growth.',
          sanitizedContent:
            'Renewable energy technology advancements are setting the stage for a vibrant and sustainable future. Key players such as Tesla and SolarCity are steering this change.',
          leoSummary: {
            sentences: [
              {
                text: 'Renewable energy sees boost from technology firms.',
                score: 0.88,
              },
            ],
          },
          openAiSummary:
            'New sustainable technologies in renewable energy gain momentum, backed by substantial investments.',
          thriveCompanies: [
            {
              id: 'comp789',
              name: 'EcoPower Innovations',
              logoUrl: 'https://example.com/eco-logos/logo789.png',
            },
          ],
        },
      ],
    },
    task_input_hash: '32376d93e35b7f6db685ba7ea8f105ce',
    task_output: {
      type: 'array',
      items: [
        {
          companyName: 'EcoPower Innovations',
          companyId: 'comp789',
          logoUrl: 'https://example.com/eco-logos/logo789.png',
          articleCollections: [
            {
              topic: 'Renewable Energy',
              summary:
                'The article discusses the latest advancements and the rising investment in the field of renewable energy.',
              articles: [
                {
                  title: 'Innovations in Renewable Energy',
                  url: 'https://greenlight.com/renewable-energy',
                  author: 'Emily Rose',
                  source: 'GreenTech Magazine',
                  published: 1627737600,
                  sentiment: 'positive',
                  businessEvents: [
                    {
                      label: 'Green Energy Tech',
                      salienceLevel: 'High',
                    },
                  ],
                },
              ],
            },
          ],
        },
      ],
    },
    task_output_hash: '601fc8c05ebabc27334169824bc53c99',
    group: {
      // id: 'f87b09782264e72e9b171f9ae4180090',
      iteration: 2,
      properties: {
        model: 'gpt-4-turbo-2024-04-09',
        provider: 'openai',
        name: 'WorkflowAI',
        runner_name: 'WorkflowAI',
        runner_version: '2d3865b4c9a6b5801f519769c1a6f3d1',
        variant_id: 'cfecb7657a68aaee88b903f0debc0ab2',
      },
      tags: [
        'model=gpt-4-turbo-2024-04-09',
        'name=WorkflowAI',
        'provider=openai',
      ],
    },
    start_time: '2024-04-25T09:59:29.952000Z',
    end_time: '2024-04-25T09:59:45.083000Z',
    duration_seconds: 15.130454,
    created_at: '2024-04-24T15:58:03.551754',
    example_id: null,
    corrections: null,
  },
  taskSchemaImage: {
    version: 'e06fcc2cd17bf2a621cdf7cdddff305d',
    json_schema: {
      $defs: {
        Image: {
          properties: {
            name: {
              description: 'An optional',
              title: 'Name',
              type: 'string',
            },
            content_type: {
              description: 'The content type of the image',
              examples: ['image/png', 'image/jpeg'],
              title: 'Content Type',
              type: 'string',
            },
            data: {
              description: 'The base64 encoded data of the image',
              title: 'Data',
              type: 'string',
            },
          },
          required: ['name', 'content_type', 'data'],
          title: 'Image',
          type: 'object',
        },
      },
      properties: {
        images: {
          allOf: [
            {
              $ref: '#/$defs/Image',
            },
          ],
          description: 'The image to classify',
        },
      },
      required: ['images'],
      title: 'MedicalBillClassificationTaskInput',
      type: 'object',
    },
  },
  taskSchemaImageArray: {
    version: '6f80c03d3fed5d0560af6c80ebc20cce',
    json_schema: {
      $defs: {
        Image: {
          properties: {
            name: {
              description: 'An optional',
              title: 'Name',
              type: 'string',
            },
            content_type: {
              description: 'The content type of the image',
              examples: ['image/png', 'image/jpeg'],
              title: 'Content Type',
              type: 'string',
            },
            data: {
              description: 'The base64 encoded data of the image',
              title: 'Data',
              type: 'string',
            },
          },
          required: ['name', 'content_type', 'data'],
          title: 'Image',
          type: 'object',
        },
      },
      properties: {
        images: {
          items: {
            $ref: '#/$defs/Image',
          },
          title: 'Images',
          type: 'array',
        },
      },
      required: ['images'],
      title: 'DemoImageTaskInput',
      type: 'object',
    },
  },
  taskInputImage: {
    images: [
      {
        name: '1.jpg',
        content_type: 'image/jpeg',
        data: 'iVBORw0KGgoAAAANSUhEUgAAAQAAAAEACAIAAADTED8xAAADMElEQVR4nOzVwQnAIBQFQYXff81RUkQCOyDj1YOPnbXWPmeTRef+/3O/OyBjzh3CD95BfqICMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMK0CMO0TAAD//2Anhf4QtqobAAAAAElFTkSuQmCC',
      },
      {
        name: '1.jpg',
        content_type: 'image/jpeg',
        data: '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',
      },
    ],
  },
};
