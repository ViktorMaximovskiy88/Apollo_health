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
  shortLabel: string;
  adminRoleRequired: boolean;
}

export const navSlice = createSlice({
  name: 'nav',
  initialState: {
    breadcrumbs: [] as Breadcrumb[],
    layout: {
      appBarPosition: 'top',
    },
    menu: {
      items: [
        { url: '/sites', label: 'Sites', shortLabel: 'Sites', adminRoleRequired: false },
        {
          url: '/documents',
          label: 'All Documents',
          shortLabel: 'Docs',
          adminRoleRequired: false,
        },
        {
          url: '/work-queues',
          label: 'Work Queues',
          shortLabel: 'Queues',
          adminRoleRequired: false,
        },
        {
          url: '/document-family',
          label: 'Document Family',
          shortLabel: 'Document Family',
          adminRoleRequired: false,
        },
        {
          url: '/payer-family',
          label: 'Payer Family',
          shortLabel: 'Payer Family',
          adminRoleRequired: false,
        },
        {
          url: '/translations',
          label: 'Translations',
          shortLabel: 'Translations',
          adminRoleRequired: false,
        },
        {
          url: '/payer-backbone',
          label: 'Payers',
          shortLabel: 'Payers',
          adminRoleRequired: true,
        },
        { url: '/users', label: 'Users', shortLabel: 'Users', adminRoleRequired: false },
        { url: '/devtools', label: 'Devtools', shortLabel: 'Devtools', adminRoleRequired: false },
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
  (state: RootState) => state.nav.breadcrumbs,
  (breadcrumbState) => breadcrumbState
);

export const menuState = createSelector(
  (state: RootState) => state.nav.menu,
  (menuState) => menuState
);

export const { actions, reducer } = navSlice;
export const { appendBreadcrumb, setBreadcrumbs, appendBreadcrumbs } = navSlice.actions;
export default navSlice;
