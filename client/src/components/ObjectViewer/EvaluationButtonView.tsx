import { Pencil, RefreshCw, Save } from 'lucide-react';
import { useCallback, useMemo, useState } from 'react';
import { FieldEvaluationOptions, ObjectKeyType } from '@/lib/schemaUtils';
import { Button } from '../ui/Button';

type EvaluationButtonViewProps = {
  fieldValue: unknown;
  fieldKey: string;
  keyPath: string;
  flatFieldBasedConfigDict?: Record<string, ObjectKeyType>;
  flatFieldBasedConfigMode?: 'editable' | 'readonly' | 'evaluation';
  isHovering: boolean;
  onEdit: ((keyPath: string, newVal: unknown, triggerSave?: boolean) => void) | undefined;
  updateEditMode: (value: boolean) => void;
  isEditModeOn: boolean;
};

export function EvaluationButtonView(props: EvaluationButtonViewProps) {
  const {
    fieldValue,
    fieldKey,
    keyPath,
    flatFieldBasedConfigDict,
    flatFieldBasedConfigMode,
    isHovering,
    onEdit,
    updateEditMode,
    isEditModeOn,
  } = props;

  const rootFieldKeyPath = useMemo(() => {
    if (keyPath) {
      if (Number(fieldKey) !== undefined) {
        return keyPath + '.0';
      }
      return keyPath + '.' + fieldKey;
    }
    return fieldKey;
  }, [fieldKey, keyPath]);

  const rootFlatFieldBasedConfigEntry = useMemo(() => {
    const result = flatFieldBasedConfigDict?.[rootFieldKeyPath];
    if (result?.type === 'object') {
      return undefined;
    }
    return result;
  }, [rootFieldKeyPath, flatFieldBasedConfigDict]);

  const fieldKeyPath = useMemo(() => {
    if (keyPath) {
      return keyPath + '.' + fieldKey;
    }
    return fieldKey;
  }, [fieldKey, keyPath]);

  const flatFieldBasedConfigEntry = useMemo(() => {
    const result = flatFieldBasedConfigDict?.[fieldKeyPath];
    if (result?.type === 'object') {
      return undefined;
    }
    return result;
  }, [fieldKeyPath, flatFieldBasedConfigDict]);

  const [isHoveringOverEditButton, setIsHoveringOverEditButton] = useState(false);

  const shouldShowEditButton = useMemo(() => {
    if (isEditModeOn) {
      return false;
    }

    if (flatFieldBasedConfigMode !== 'evaluation') {
      return false;
    }

    return isHovering || isHoveringOverEditButton;
  }, [flatFieldBasedConfigMode, isHovering, isHoveringOverEditButton, isEditModeOn]);

  const shouldShowResetButton = useMemo(() => {
    if (isEditModeOn) {
      return false;
    }

    if (flatFieldBasedConfigMode !== 'evaluation' || shouldShowEditButton) {
      return false;
    }

    if (
      rootFlatFieldBasedConfigEntry?.value === FieldEvaluationOptions.SEMANTICALLY_EQUAL ||
      flatFieldBasedConfigEntry?.value === FieldEvaluationOptions.SEMANTICALLY_EQUAL
    ) {
      return true;
    }

    return false;
  }, [
    flatFieldBasedConfigMode,
    rootFlatFieldBasedConfigEntry,
    flatFieldBasedConfigEntry,
    shouldShowEditButton,
    isEditModeOn,
  ]);

  const onSave = useCallback(() => {
    onEdit?.(fieldKeyPath, fieldValue, true);
    setIsHoveringOverEditButton(false);
    updateEditMode(false);
  }, [updateEditMode, fieldValue, fieldKeyPath, onEdit]);

  if (!shouldShowEditButton && !shouldShowResetButton && !isEditModeOn) {
    return null;
  }

  const saveButton = (
    <div className='pl-2'>
      <Button
        onClick={onSave}
        icon={<Save size={16} strokeWidth={3} />}
        className='rounded-[10px] h-[31px] items-center justify-center'
      >
        Save
      </Button>
    </div>
  );

  const editButton = (
    <div
      className='pl-2'
      onMouseEnter={() => setIsHoveringOverEditButton(true)}
      onMouseLeave={() => setIsHoveringOverEditButton(false)}
    >
      <Button
        onClick={() => updateEditMode(true)}
        icon={<Pencil size={16} strokeWidth={3} />}
        className='rounded-[10px] h-[31px] items-center justify-center'
      >
        Edit
      </Button>
    </div>
  );

  const resetButton = (
    <Button
      onClick={() => onEdit?.(fieldKeyPath, undefined, true)}
      icon={<RefreshCw size={16} strokeWidth={3} />}
      className='rounded-[10px] h-[31px] w-[31px] items-center justify-center p-0 ml-2'
    />
  );

  return (
    <div className='flex gap-1'>
      {shouldShowEditButton && editButton}
      {isEditModeOn && saveButton}
      {shouldShowResetButton && resetButton}
    </div>
  );
}
