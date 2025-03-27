import { beautifyTypescript } from '@/code-generator/beautify';
import { JsonSchema } from '@/types';
import { schemaToTS } from './schemaToTS';

/**
 * Transform a string into a valid TS/JS var name
 * Not strict.
 * @param text any text, like a task ID for example
 */
const validVarName = (text: string): string => {
  // Remove dashes and spaces by concatenating and upper casing
  const noDashes = text
    .trim()
    .split(/-|\s/)
    .map((part) => `${part.substring(0, 1).toUpperCase()}${part.substring(1)}`)
    .join('');

  // Replace any invalid character by an underscore
  const anyCase = noDashes.replace(/[^a-z0-9_$]/gi, '_').replace(/_{2,}/g, '_');

  // Strip leading digits and force the first character to be lower case
  const withoutLeadingDigits = anyCase.replace(/^[0-9]+/, '');

  // If stripping digits left an empty string, return a default name
  if (!withoutLeadingDigits) {
    return 'var';
  }

  return `${withoutLeadingDigits.substring(0, 1).toLowerCase()}${withoutLeadingDigits.substring(1)}`;
};

type GeneratedCode = {
  language: 'bash' | 'typescript';
  code: string;
};

type GetPlaygroundSnippetsConfig = {
  taskId: string;
  taskName?: string;
  schema: {
    id: number;
    input: JsonSchema;
    output: JsonSchema;
  };
  version: number | string;
  example: {
    input: Record<string, unknown>;
    output: Record<string, unknown>;
  };
  api?: {
    url?: string | null | undefined;
  };
  descriptionAsComments?: boolean;
  secondaryInput?: Record<string, unknown>;
};

type GetPlaygroundSnippetsResult = {
  installSdk: GeneratedCode;
  initializeClient: GeneratedCode;
  initializeTask: GeneratedCode;
  runTask: GeneratedCode;
  streamRunTask: GeneratedCode;
};

function installSDKCode() {
  return `npm install @workflowai/workflowai       # npm
yarn add @workflowai/workflowai          # yarn`;
}

function imports(extras: Set<string> | undefined) {
  const others = !extras || !extras.size ? '' : ['', ...extras].join(', ');

  return `import { WorkflowAI${others} } from "@workflowai/workflowai"`;
}

function initializeClientCode(
  api:
    | {
        url?: string | null;
      }
    | undefined
) {
  return `const workflowAI = new WorkflowAI({${
    api?.url
      ? `
    url: "${api.url}",`
      : ''
  }
    // optional, defaults to process.env.WORKFLOWAI_API_KEY
    // key: // Add your API key here
  })`;
}

function addPrefixToEachLine(str: string, prefix: string) {
  return str
    .split('\n')
    .map((line) => `${prefix}${line}`)
    .join('\n');
}

function runTaskCode(taskFunctionName: string, baseTypeName: string, beautifiedInput: string, secondaryInput?: string) {
  const firstInput = `const input: ${baseTypeName}Input = ${beautifiedInput}`;
  const secondInput = secondaryInput
    ? addPrefixToEachLine(`const input: ${baseTypeName}Input = ${secondaryInput}`, '  //')
    : '';

  return `

async function ${taskFunctionName}Run() {
${addPrefixToEachLine(firstInput, '  ')}${secondInput ? '\n' : ''}${secondInput}

  try {
    const {
      output,
      data: { duration_seconds, cost_usd, version },
    } = await ${taskFunctionName}(input)

    console.log(output)
    console.log("\\nModel: ", version?.properties?.model)
    console.log("Cost: $", cost_usd)
    console.log("Latency: ", duration_seconds?.toFixed(2), "s")
  } catch (error) {
    console.error('Failed to run :', error)
  }
}

${taskFunctionName}Run()`;
}

function initializeTaskCode(
  baseTypeName: string,
  taskFunctionName: string,
  schema: Record<string, unknown>,
  taskId: string,
  version: number | string,
  inputTS: string,
  outputTS: string
) {
  return beautifyTypescript(`${inputTS}
${outputTS}

const ${taskFunctionName} = workflowAI.agent<${baseTypeName}Input, ${baseTypeName}Output>({
  id: "${taskId}",
  schemaId: ${schema.id},
  version: ${version},
  // Cache options:
  // - "auto" (default): if a previous run exists with the same version and input, and if
  // the temperature is 0, the cached output is returned
  // - "always": the cached output is returned when available, regardless
  // of the temperature value
  // - "never": the cache is never used
  useCache: "auto"
})`);
}

function toPascalCase(str: string) {
  return str.replace(/(^\w|-\w)/g, (match) => match.toUpperCase().replace(/-/, ''));
}

export const getPlaygroundSnippets = async (
  config: GetPlaygroundSnippetsConfig
): Promise<GetPlaygroundSnippetsResult> => {
  const {
    taskId,
    taskName,
    schema,
    version,
    example,
    api,

    secondaryInput,
  } = {
    ...config,
  };

  const taskFunctionName = validVarName(taskName || taskId);
  const baseTypeName = toPascalCase(taskFunctionName);
  const _stringifiedInput = JSON.stringify(example.input, null, 2);
  const { compiled: inputTS, existingWAIRefs: inputRefs } = await schemaToTS(baseTypeName + 'Input', schema.input);
  const { compiled: outputTS, existingWAIRefs: outputRefs } = await schemaToTS(baseTypeName + 'Output', schema.output);
  // Unioning the sets
  for (const ref of outputRefs) {
    inputRefs.add(ref);
  }

  return {
    installSdk: {
      language: 'bash',
      code: installSDKCode(),
    },

    initializeClient: {
      language: 'typescript',
      code: [imports(inputRefs), initializeClientCode(api)].join('\n\n'),
    },

    initializeTask: {
      language: 'typescript',
      code: initializeTaskCode(baseTypeName, taskFunctionName, schema, taskId, version, inputTS, outputTS),
    },

    runTask: {
      language: 'typescript',
      code: `

${runTaskCode(
  taskFunctionName,
  baseTypeName,
  _stringifiedInput,
  secondaryInput ? JSON.stringify(secondaryInput, null, 2) : undefined
)}
`.trim(),
    },

    streamRunTask: {
      language: 'typescript',
      code: `

const input: ${baseTypeName}Input = ${_stringifiedInput}

async function ${taskFunctionName}Run() {
  try {
    const { stream } = await ${taskFunctionName}(input).stream()

    for await (const { output } of stream) {
      // A partial output, as it becomes available
      console.log(output)
    }
  } catch (error) {
      console.error(error)
  }
}

${taskFunctionName}Run()
`.trim(),
    },
  };
};
