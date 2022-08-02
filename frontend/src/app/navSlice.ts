import 'urlpattern-polyfill';
import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from './store';

interface Breadcrumb {
  url: string;
  label: string;
}

interface MenuItem {
  url: string;
  label: string;
}

export const navSlice = createSlice({
  name: 'nav',
  initialState: {
    breadcrumbs: [] as Breadcrumb[],
    layout: {
      appBarPosition: 'left',
    },
    menu: {
      items: [
        { url: '/sites', label: 'Sites' },
        { url: '/work-queues', label: 'Work Queues' },
        {
          url: '/documents',
          label: 'All Documents',
        },
        { url: '/users', label: 'Users' },
      ] as MenuItem[],
      currentItem: {} as MenuItem,
    },
  },
  reducers: {
    setBreadcrumbs: (state, action: PayloadAction<Breadcrumb[]>) => {
      state.breadcrumbs = [...action.payload];
    },
    appendBreadcrumb: (state, action: PayloadAction<Breadcrumb>) => {
      state.breadcrumbs = [...state.breadcrumbs, action.payload];
    },
    appendBreadcrumbs: (state, action: PayloadAction<Breadcrumb[]>) => {
      state.breadcrumbs = [...state.breadcrumbs, ...action.payload];
    },
    toggleAppBarPosition: (state) => {
      console.log(state.layout.appBarPosition);
      state.layout.appBarPosition = state.layout.appBarPosition == 'top' ? 'left' : 'top';
    },
  },
});

export const breadcrumbState = createSelector(
  (state: RootState) => state.nav.breadcrumbs,
  (breadcrumbState) => breadcrumbState
);

export const menuState = createSelector(
  (state: RootState) => state.nav.menu,
  (menuState) => menuState
);

export const layoutState = createSelector(
  (state: RootState) => state.nav.layout,
  (layout) => layout
);

export const { actions, reducer } = navSlice;
export const { appendBreadcrumb, setBreadcrumbs, appendBreadcrumbs, toggleAppBarPosition } =
  navSlice.actions;
export default navSlice;
