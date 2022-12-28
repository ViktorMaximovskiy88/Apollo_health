import { MiddlewareAPI, isRejectedWithValue, Middleware } from '@reduxjs/toolkit';

import settings from '../settings';

const logout = () => {
  // TODO scopes when we make that decision...
  const localStorageKey = `@@auth0spajs@@::${settings.auth0.clientId}::${settings.auth0.audience}::openid profile email`;
  const cookieKey = `auth0.${settings.auth0.clientId}.is.authenticated`;
  localStorage.removeItem(localStorageKey);
  document.cookie = `${cookieKey}=;expires=${new Date(0).toUTCString()}`;
  window.location.href = settings.auth0.domain;
};

export const rtkAuth: Middleware = (api: MiddlewareAPI) => (next) => (action) => {
  if (isRejectedWithValue(action)) {
    const { status } = action.payload;
    if (status === 401) {
      logout();
    } else if (status === 403) {
      window.location.href = `${window.location.origin}/request-access`;
    }
  }

  return next(action);
};
