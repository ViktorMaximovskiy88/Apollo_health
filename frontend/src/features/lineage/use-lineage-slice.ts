import { useSelector, useDispatch } from 'react-redux';
import { lineageSelector, actions } from './lineage-slice';

export default function useLineageSlice() {
  const state = useSelector(lineageSelector);
  const dispatch = useDispatch();
  return {
    state,
    actions: {
      setLeftSide: (args: any) => dispatch(actions.setLeftSide(args)),
      setRightSide: (args: any) => dispatch(actions.setRightSide(args)),
      toggleSingularLineage: () => dispatch(actions.toggleSingularLineage()),
      toggleMultipleLineage: () => dispatch(actions.toggleMultipleLineage()),
      toggleMissingLineage: () => dispatch(actions.toggleMissingLineage()),
      toggleCollapsed: (args: any) => dispatch(actions.toggleCollapsed(args)),
      setCollapsed: (args: any) => dispatch(actions.setCollapsed(args)),
      onSearch: (args: any) => dispatch(actions.onSearch(args)),
    },
  };
}
