import { arrayObjectSchemaFixture } from '@/tests/fixtures/schemaEditor/arrayObject';
import { defaultInputObjectSchemaFixture } from '@/tests/fixtures/schemaEditor/defaultInputObjects';
import { defaultOutputObjectSchemaFixture } from '@/tests/fixtures/schemaEditor/defaultOutputObject';
import { fileSchemaDefinitionFixtures, fileSchemaFixture } from '@/tests/fixtures/schemaEditor/fileSchema';
import { productionObjectsSchemaFixture } from '@/tests/fixtures/schemaEditor/productionObject';
import {
  refArrayObjectDefinitionFixtures,
  refArrayObjectsSchemaFixture,
} from '@/tests/fixtures/schemaEditor/refArrayObject';
import { refObjectDefinitionFixtures, refObjectsSchemaFixture } from '@/tests/fixtures/schemaEditor/refObjects';
import { simpleObjectSchemaFixture } from '@/tests/fixtures/schemaEditor/simpleObject';
import { unionObjectsSchemaFixture } from '@/tests/fixtures/schemaEditor/unionObjects';
import { JsonSchema } from '@/types';
import { untypedObjectSchemaFixture } from '../tests/fixtures/schemaEditor/untypedObject';
import {
  areSchemasEquivalent,
  fromSchemaToSplattedEditorFields,
  fromSplattedEditorFieldsToSchema,
} from './schemaEditorUtils';

describe('schemaEditorUtils', () => {
  describe('fromSchemaToSplattedEditorFields', () => {
    it('should convert object schema to splatted editor fields | simple cases', () => {
      const result = fromSchemaToSplattedEditorFields(simpleObjectSchemaFixture.originalSchema);
      expect(result).toEqual(simpleObjectSchemaFixture.splattedEditorFields);
    });

    it('should convert object schema to splatted editor fields | union objects', () => {
      const result = fromSchemaToSplattedEditorFields(unionObjectsSchemaFixture.originalSchema);
      expect(result).toEqual(unionObjectsSchemaFixture.splattedEditorFields);
    });

    it('should convert object schema to splatted editor fields | ref objects', () => {
      const result = fromSchemaToSplattedEditorFields(
        refObjectsSchemaFixture.originalSchema,
        '',
        refObjectDefinitionFixtures.originalDefinitions
      );
      expect(result).toEqual(refObjectsSchemaFixture.splattedEditorFields);
    });

    it('should convert object schema to splatted editor fields | ref array objects', () => {
      const result = fromSchemaToSplattedEditorFields(
        refArrayObjectsSchemaFixture.originalSchema,
        '',
        refArrayObjectDefinitionFixtures.originalDefinitions
      );
      expect(result).toEqual(refArrayObjectsSchemaFixture.splattedEditorFields);
    });

    it('should convert object schema to splatted editor fields | array objects', () => {
      const result = fromSchemaToSplattedEditorFields(arrayObjectSchemaFixture.originalSchema);
      expect(result).toEqual(arrayObjectSchemaFixture.splattedEditorFields);
    });

    it('should convert object schema to splatted editor fields | production objects', () => {
      const result = fromSchemaToSplattedEditorFields(productionObjectsSchemaFixture.originalSchema);
      expect(result).toEqual(productionObjectsSchemaFixture.splattedEditorFields);
    });

    it('should convert object schema to splatted editor fields | default input objects', () => {
      const result = fromSchemaToSplattedEditorFields(defaultInputObjectSchemaFixture.originalSchema);
      expect(result).toEqual(defaultInputObjectSchemaFixture.splattedEditorFields);
    });

    it('should convert object schema to splatted editor fields | default output objects', () => {
      const result = fromSchemaToSplattedEditorFields(defaultOutputObjectSchemaFixture.originalSchema);
      expect(result).toEqual(defaultOutputObjectSchemaFixture.splattedEditorFields);
    });

    it('should convert object schema to splatted editor fields | untyped objects', () => {
      const result = fromSchemaToSplattedEditorFields(untypedObjectSchemaFixture.originalSchema);
      expect(result).toEqual(untypedObjectSchemaFixture.splattedEditorFields);
    });

    it('should convert object schema to splatted editor fields | file schema', () => {
      const result = fromSchemaToSplattedEditorFields(
        fileSchemaFixture.originalSchema,
        '',
        fileSchemaDefinitionFixtures.originalDefinitions
      );
      expect(result).toEqual(fileSchemaFixture.splattedEditorFields);
    });
  });

  describe('fromSplattedEditorFieldsToSchema', () => {
    it('should convert splatted editor fields to object schema | simple cases', () => {
      const { schema: result } = fromSplattedEditorFieldsToSchema(simpleObjectSchemaFixture.splattedEditorFields);
      expect(result).toEqual(simpleObjectSchemaFixture.finalSchema);
    });

    it('should convert splatted editor fields to object schema | union objects', () => {
      const { schema: result } = fromSplattedEditorFieldsToSchema(unionObjectsSchemaFixture.splattedEditorFields);
      expect(result).toEqual(unionObjectsSchemaFixture.finalSchema);
    });

    it('should convert splatted editor fields to object schema | ref objects', () => {
      const { schema: result, definitions } = fromSplattedEditorFieldsToSchema(
        refObjectsSchemaFixture.splattedEditorFields
      );
      expect(result).toEqual(refObjectsSchemaFixture.finalSchema);
      expect(definitions).toEqual(refObjectDefinitionFixtures.finalDefinitions);
    });

    it('should convert splatted editor fields to object schema | ref array objects', () => {
      const { schema: result, definitions } = fromSplattedEditorFieldsToSchema(
        refArrayObjectsSchemaFixture.splattedEditorFields
      );
      expect(result).toEqual(refArrayObjectsSchemaFixture.finalSchema);
      expect(definitions).toEqual(refArrayObjectDefinitionFixtures.finalDefinitions);
    });

    it('should convert splatted editor fields to object schema | array objects', () => {
      const { schema: result } = fromSplattedEditorFieldsToSchema(arrayObjectSchemaFixture.splattedEditorFields);
      expect(result).toEqual(arrayObjectSchemaFixture.finalSchema);
    });

    it('should convert splatted editor fields to object schema | production objects', () => {
      const { schema: result } = fromSplattedEditorFieldsToSchema(productionObjectsSchemaFixture.splattedEditorFields);
      expect(result).toEqual(productionObjectsSchemaFixture.finalSchema);
    });

    it('should convert splatted editor fields to object schema | default input objects', () => {
      const { schema: result } = fromSplattedEditorFieldsToSchema(defaultInputObjectSchemaFixture.splattedEditorFields);
      expect(result).toEqual(defaultInputObjectSchemaFixture.finalSchema);
    });

    it('should convert splatted editor fields to object schema | default output objects', () => {
      const { schema: result } = fromSplattedEditorFieldsToSchema(
        defaultOutputObjectSchemaFixture.splattedEditorFields
      );
      expect(result).toEqual(defaultOutputObjectSchemaFixture.finalSchema);
    });

    it('should convert splatted editor fields to object schema | untyped objects', () => {
      const { schema: result } = fromSplattedEditorFieldsToSchema(untypedObjectSchemaFixture.splattedEditorFields);
      expect(result).toEqual(untypedObjectSchemaFixture.finalSchema);
    });

    it('should convert splatted editor fields to object schema | file schema', () => {
      const { schema: result, definitions } = fromSplattedEditorFieldsToSchema(fileSchemaFixture.splattedEditorFields);
      expect(result).toEqual(fileSchemaFixture.finalSchema);
      expect(definitions).toEqual(fileSchemaDefinitionFixtures.finalDefinitions);
    });

    describe('areSchemasEquivalent', () => {
      it('should return true if schemas are equivalent', () => {
        const schema1: JsonSchema = {
          type: 'object',
          properties: {
            name: {
              type: 'string',
            },
          },
        };

        expect(areSchemasEquivalent(schema1, schema1)).toBe(true);
      });

      it('should return false if schemas are not equivalent', () => {
        const schema1: JsonSchema = {
          type: 'object',
          properties: {
            name: {
              type: 'string',
            },
          },
        };
        const schema2: JsonSchema = {
          type: 'object',
          properties: {
            name: {
              type: 'number',
            },
          },
        };
        expect(areSchemasEquivalent(schema1, schema2)).toBe(false);
      });

      it('should avoid comparing specific $defs', () => {
        const schema1: JsonSchema = {
          type: 'object',
          properties: {
            image: {
              $ref: '#/$defs/Image',
            },
          },
        };
        const schema2: JsonSchema = {
          $defs: {
            Image: {
              type: 'string',
            },
          },
          type: 'object',
          properties: {
            image: {
              $ref: '#/$defs/Image',
            },
          },
        };
        expect(areSchemasEquivalent(schema1, schema2)).toBe(true);
      });
    });
  });
});
