import { JsonObjectSchema } from '@/types';

export const TEST_IMAGE_SCHEMA: JsonObjectSchema = {
  properties: {
    url: {
      description: 'A url for the image',
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
  title: 'Image',
  type: 'object',
};
