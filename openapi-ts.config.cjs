/** @type {import('@hey-api/openapi-ts').UserConfig} */
module.exports = {
  input: 'backend-types/openapi_fixed.json',
  output: 'src/types/workflowAI',
  exportCore: false,
  exportSchemas: false,
  exportServices: false,
};
