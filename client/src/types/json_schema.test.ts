import { taskSchemaFixture } from '@/tests/fixtures/taskSchema';
import { getSubSchema } from './json_schema';

const { simpleSchema } = taskSchemaFixture;

describe('json_schema', () => {
  describe('getSubSchema', () => {
    it('correctly handlers refs', () => {
      const value = getSubSchema(simpleSchema, simpleSchema.$defs, 'event_category');
      expect(value.type).toEqual('string');
    });

    it('parses properties', () => {
      const value = getSubSchema(simpleSchema, simpleSchema.$defs, 'event_participants_emails_addresses');
      expect(value).toBeTruthy();
    });

    it('extracts enums', () => {
      const value = getSubSchema(simpleSchema, simpleSchema.$defs, 'event_category');
      expect(value).toEqual({
        enum: ['UNSPECIFIED', 'IN_PERSON_MEETING', 'REMOTE_MEETING', 'FLIGHT', 'TO_DO', 'BIRTHDAY'],
        title: 'CalendarEventCategory',
        type: 'string',
        nullable: true,
        followedRefName: 'CalendarEventCategory',
      });
    });

    it('follows refs and sets followedRefName', () => {
      const value = getSubSchema(
        taskSchemaFixture.taskSchemaImage.json_schema,
        taskSchemaFixture.taskSchemaImage.json_schema.$defs,
        'images'
      );
      expect(value).toEqual({
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
        followedRefName: 'Image',
        nullable: false,
      });
    });
  });
});
