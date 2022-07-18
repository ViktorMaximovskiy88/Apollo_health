import {
  setBreadcrumbs,
  appendBreadcrumb,
  appendBreadcrumbs,
  breadcrumbState,
  menuState,
} from './appSlice';
import { useDispatch, useSelector } from 'react-redux';

const useAppStore = () => {
  const dispatch = useDispatch();
  const breadcrumbs = useSelector(breadcrumbState);
  const menu = useSelector(menuState);

  return {
    state: {
      breadcrumbs,
      menu,
    },
    actions: {
      setBreadcrumbs: (payload: any) => dispatch(setBreadcrumbs(payload)),
      appendBreadcrumb: (payload: any) => dispatch(appendBreadcrumb(payload)),
      appendBreadcrumbs: (payload: any) => dispatch(appendBreadcrumbs(payload)),
    },
  };
};

export default useAppStore;
