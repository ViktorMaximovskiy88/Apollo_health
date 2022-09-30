import { useSelector, useDispatch } from 'react-redux';
import { lineageSelector, actions } from './lineage-slice';
import _ from 'lodash';

export default function useLineage() {
  const state = useSelector(lineageSelector);
  const dispatch = useDispatch();
  return {
    state,
    actions: {
      setLeftSide: (args: any) => dispatch(actions.setLeftSide(args)),
      setRightSide: (args: any) => dispatch(actions.setRightSide(args)),
    },
  };
}
