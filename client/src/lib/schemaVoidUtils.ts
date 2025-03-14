import { cloneDeep, mergeWith } from 'lodash';
import { GeneralizedTaskInput } from '@/types';

function customizer(objValue: unknown, srcValue: unknown) {
  if (objValue !== undefined) {
    return objValue;
  }
  return srcValue;
}

export function mergeTaskInputAndVoid(
  taskInput: GeneralizedTaskInput,
  voidInput: GeneralizedTaskInput | undefined
) {
  if (Array.isArray(taskInput) || !voidInput) return taskInput;
  return mergeWith(cloneDeep(taskInput), voidInput, customizer);
}
