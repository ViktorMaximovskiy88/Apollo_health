import { useCallback, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { TypeOnSelectionChangeArg } from '@inovua/reactdatagrid-community/types/TypeDataGridProps';

export const useDataTableSelection = (
  tableStateSelector: any,
  setTableSelect: (select: TypeOnSelectionChangeArg) => void
) => {
  const dispatch = useDispatch();
  const { selection }: { selection: TypeOnSelectionChangeArg } = useSelector(tableStateSelector);
  const onSelectionChange = useCallback(
    (select: TypeOnSelectionChangeArg) => dispatch(setTableSelect(select)),
    [dispatch, setTableSelect]
  );
  return useMemo(
    () => ({
      selected: selection?.selected,
      unselected: selection?.unselected as any,
      onSelectionChange,
    }),
    [selection, onSelectionChange]
  );
};
