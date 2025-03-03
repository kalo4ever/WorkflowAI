/* eslint-disable @typescript-eslint/no-explicit-any */
/* eslint-disable @typescript-eslint/no-var-requires */

const fs = require('fs');

// Define types for better TypeScript support
type Schema = {
  [key: string]: any;
  components?: {
    schemas?: { [key: string]: unknown };
  };
};

// URL of the remote OpenAPI schema
const schemaUrl = 'https://api.workflowai.dev/openapi.json';
const outputPath = './backend-types/openapi_fixed.json';

// Function to recursively find and replace $defs with $ref
function replaceDefsWithRefs(obj: Schema, rootSchema: Schema = obj) {
  if (Array.isArray(obj)) {
    obj.forEach((item) => replaceDefsWithRefs(item, rootSchema));
  } else if (typeof obj === 'object' && obj !== null) {
    for (const key in obj) {
      if (key === '$defs') {
        // Move each $defs item to components/schemas
        for (const defName in obj[key]) {
          rootSchema.components!.schemas![defName] = obj[key][defName];
        }
        // Delete $defs after moving
        delete obj[key];
      } else if (
        key === '$ref' &&
        typeof obj[key] === 'string' &&
        obj[key].startsWith('#/$defs/')
      ) {
        // Update $ref to point to components/schemas
        obj[key] = obj[key].replace('#/$defs/', '#/components/schemas/');
      } else {
        replaceDefsWithRefs(obj[key], rootSchema);
      }
    }
  }
}

async function fetchAndProcessSchema() {
  try {
    // Fetch the OpenAPI schema from the remote URL using fetch
    const response = await fetch(schemaUrl);
    if (!response.ok) {
      throw new Error(`Failed to fetch schema: ${response.statusText}`);
    }

    const schema: Schema = await response.json();

    // Ensure components.schemas exists
    if (!schema.components) {
      schema.components = {};
    }
    if (!schema.components.schemas) {
      schema.components.schemas = {};
    }

    // Replace $defs and $refs throughout the schema
    replaceDefsWithRefs(schema);

    // Write the updated schema to a new file
    fs.writeFile(
      outputPath,
      JSON.stringify(schema, null, 2),
      'utf8',
      (err: any) => {
        if (err) {
          console.error('Error writing the fixed file:', err);
          return;
        }
      }
    );
  } catch (error) {
    console.error('Error fetching or processing the schema:', error);
  }
}

// Execute the function to fetch and process the schema
fetchAndProcessSchema();
