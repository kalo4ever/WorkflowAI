import { SearchFieldParam } from '@/lib/routeFormatter';
import { SearchFields } from '@/types/workflowAI';

export function findHints(
  param: SearchFieldParam,
  fieldName: string | undefined,
  searchFields: SearchFields | undefined
): string[] | undefined {
  if (!searchFields) return undefined;

  if (param === SearchFieldParam.FieldNames) {
    return searchFields.fields.map((field) => field.field_name);
  }

  if (!fieldName) return undefined;

  const searchField = searchFields.fields.find(
    (field) => field.field_name === fieldName
  );

  switch (param) {
    case SearchFieldParam.Operators:
      return searchField?.operators;
    case SearchFieldParam.Values:
      return !!searchField?.suggestions
        ? searchField.suggestions.map(String)
        : undefined;
  }
}

export function findAndFilterHints(
  param: SearchFieldParam,
  fieldName: string | undefined,
  searchFields: SearchFields | undefined,
  text: string
): string[] | undefined {
  const hints = findHints(param, fieldName, searchFields);

  if (!hints) return [];
  return hints.filter((hint) =>
    hint.toLowerCase().includes(text.toLowerCase())
  );
}

function areAllFieldsSet(
  fieldNames: string[] | undefined,
  operators: string[] | undefined,
  values: string[] | undefined
): boolean {
  if (!fieldNames || !operators || !values) return false;
  if (fieldNames.length === 0) return false;

  return (
    fieldNames.length === operators.length &&
    fieldNames.length === values.length
  );
}

export function areAllFieldsSetInParams(
  params: Record<string, string | undefined>
): boolean {
  return areAllFieldsSet(
    params[SearchFieldParam.FieldNames]?.split(','),
    params[SearchFieldParam.Operators]?.split(','),
    params[SearchFieldParam.Values]?.split(',')
  );
}

export function add(
  params: Record<string, string | undefined>,
  fieldName: string,
  operator: string | undefined,
  value: string | undefined
): Record<string, string | undefined> {
  const newParams = { ...params };

  let fieldNames = newParams[SearchFieldParam.FieldNames]?.split(',') ?? [];
  let operators = newParams[SearchFieldParam.Operators]?.split(',') ?? [];
  let values = newParams[SearchFieldParam.Values]?.split(',') ?? [];

  if (
    !areAllFieldsSet(fieldNames, operators, values) &&
    fieldNames.length > 0
  ) {
    const smallestLength = Math.min(
      fieldNames.length,
      operators.length,
      values.length
    );
    fieldNames = fieldNames.slice(0, smallestLength);
    operators = operators.slice(0, smallestLength);
    values = values.slice(0, smallestLength);
  }

  fieldNames.push(fieldName);
  if (operator) operators.push(operator);
  if (value) values.push(value);

  newParams[SearchFieldParam.FieldNames] =
    fieldNames.length > 0 ? fieldNames.join(',') : undefined;
  newParams[SearchFieldParam.Operators] =
    operators.length > 0 ? operators.join(',') : undefined;
  newParams[SearchFieldParam.Values] =
    values.length > 0 ? values.join(',') : undefined;

  return newParams;
}

export function remove(
  index: number,
  params: Record<string, string | undefined>
): Record<string, string | undefined> {
  const newParams = { ...params };

  const fieldNames = newParams[SearchFieldParam.FieldNames]?.split(',');
  const operators = newParams[SearchFieldParam.Operators]?.split(',');
  const values = newParams[SearchFieldParam.Values]?.split(',');

  fieldNames?.splice(index, 1);
  operators?.splice(index, 1);
  values?.splice(index, 1);

  newParams[SearchFieldParam.FieldNames] =
    !!fieldNames && fieldNames.length > 0 ? fieldNames.join(',') : undefined;

  newParams[SearchFieldParam.Operators] =
    !!operators && operators.length > 0 ? operators.join(',') : undefined;

  newParams[SearchFieldParam.Values] =
    !!values && values.length > 0 ? values.join(',') : undefined;

  return newParams;
}

export function exchange(
  key: string,
  text: string | undefined,
  index: number,
  params: Record<string, string | undefined>
): Record<string, string | undefined> {
  const paramForKey = params[key];
  const allEntriesInParamForKey = paramForKey?.split(',') ?? [];

  if (index >= 0 && index < allEntriesInParamForKey.length) {
    if (text) {
      allEntriesInParamForKey[index] = text;
    } else {
      allEntriesInParamForKey.splice(index, 1);
    }
  } else if (text) {
    allEntriesInParamForKey.push(text);
  }

  const newParams = { ...params };

  if (allEntriesInParamForKey.length === 0) {
    newParams[key] = undefined;
  } else {
    const newParamForKey = allEntriesInParamForKey.join(',');
    newParams[key] = newParamForKey;
  }

  return newParams;
}

export function findCurrentParamToEnter(
  fieldNames: string[] | undefined,
  operators: string[] | undefined,
  values: string[] | undefined
): SearchFieldParam {
  if (!fieldNames) return SearchFieldParam.FieldNames;
  if (!operators) return SearchFieldParam.Operators;
  if (!values) return SearchFieldParam.Values;

  if (fieldNames.length === 0) return SearchFieldParam.FieldNames;
  if (values.length < operators.length) return SearchFieldParam.Values;
  if (operators.length < fieldNames.length) return SearchFieldParam.Operators;

  return SearchFieldParam.FieldNames;
}

export function findActiveIndex(
  fieldNames: string[] | undefined,
  operators: string[] | undefined,
  values: string[] | undefined
): number {
  if (!fieldNames || !operators || !values) return 0;
  if (fieldNames.length === 0) return 0;
  if (areAllFieldsSet(fieldNames, operators, values)) return fieldNames.length;
  return fieldNames.length - 1;
}

export function findCurrentIndex(
  fieldNames: string[] | undefined,
  operators: string[] | undefined,
  values: string[] | undefined
): number {
  if (!fieldNames || !operators || !values) return 0;
  if (fieldNames.length === 0) return 0;
  return fieldNames.length - 1;
}

export function findLastDefinedKey(
  fieldNames: string[] | undefined,
  operators: string[] | undefined,
  values: string[] | undefined
): SearchFieldParam | undefined {
  if (!fieldNames || fieldNames.length === 0) return undefined;
  if (!operators || operators.length === 0) return SearchFieldParam.FieldNames;
  if (!values || values.length === 0) return SearchFieldParam.Operators;

  const array: { key: string; length: number }[] = [
    { key: SearchFieldParam.FieldNames, length: fieldNames.length },
    { key: SearchFieldParam.Operators, length: operators.length },
    { key: SearchFieldParam.Values, length: values.length },
  ];

  array.sort((a, b) => a.length - b.length);

  switch (array[0].key) {
    case SearchFieldParam.FieldNames:
      return SearchFieldParam.Values;
    case SearchFieldParam.Operators:
      return SearchFieldParam.FieldNames;
    case SearchFieldParam.Values:
      return SearchFieldParam.Operators;
  }
}

export function findLastFieldName(
  fieldNames: string[] | undefined
): string | undefined {
  if (!fieldNames || fieldNames.length === 0) return undefined;
  return fieldNames[fieldNames.length - 1];
}

export function findParametersForBadges(
  fieldNames: string[] | undefined,
  operators: string[] | undefined,
  values: string[] | undefined
): [SearchFieldParam, string][][] | undefined {
  if (!fieldNames) return undefined;

  const result: [SearchFieldParam, string][][] = [];

  fieldNames.forEach((fieldName, index) => {
    const entry: [SearchFieldParam, string][] = [];
    entry.push([SearchFieldParam.FieldNames, fieldName]);

    if (operators && operators[index]) {
      entry.push([SearchFieldParam.Operators, operators[index]]);
    }

    if (values && values[index]) {
      entry.push([SearchFieldParam.Values, values[index]]);
    }
    result.push(entry);
  });

  return result;
}
