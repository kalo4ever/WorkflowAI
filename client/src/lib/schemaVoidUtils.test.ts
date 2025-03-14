import { mergeTaskInputAndVoid } from './schemaVoidUtils';

const voidInput = {
  name: '',
  metadata: {
    title: '',
    author: '',
  },
};

const taskInputs = [
  {
    name: 'John Doe',
  },
  {
    name: 'Jane Doe',
    metadata: {
      title: 'Breaking News in Tech',
      author: 'John Doe',
    },
  },
  {},
  [{ age: 20 }],
];

const expectedResults = [
  {
    name: 'John Doe',
    metadata: {
      title: '',
      author: '',
    },
  },
  {
    name: 'Jane Doe',
    metadata: {
      title: 'Breaking News in Tech',
      author: 'John Doe',
    },
  },
  {
    name: '',
    metadata: {
      title: '',
      author: '',
    },
  },
  [{ age: 20 }],
];

describe('mergeTaskInputAndVoid', () => {
  it('should merge task input and void input', () => {
    for (let i = 0; i < taskInputs.length; i++) {
      const merged = mergeTaskInputAndVoid(taskInputs[i], voidInput);
      expect(merged).toEqual(expectedResults[i]);
    }
  });
});
