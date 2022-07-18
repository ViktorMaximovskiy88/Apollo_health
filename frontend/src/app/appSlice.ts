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

export const appSlice = createSlice({
  name: 'nav',
  initialState: {
    breadcrumbs: [] as Breadcrumb[],
    menu: {
      items: [
        { url: '/sites', label: 'Sites' },
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
  },
});

export const breadcrumbState = createSelector(
  (state: RootState) => state.app.breadcrumbs,
  (breadcrumbState) => breadcrumbState
);

export const menuState = createSelector(
  (state: RootState) => state.app.menu,
  (menuState) => menuState
);

export const { actions, reducer } = appSlice;
export const { appendBreadcrumb, setBreadcrumbs, appendBreadcrumbs } = appSlice.actions;
export default appSlice;
