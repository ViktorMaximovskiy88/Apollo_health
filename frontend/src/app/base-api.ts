import { createApi, fetchBaseQuery as defaultFetchBaseQuery } from '@reduxjs/toolkit/query/react';

import { Auth0Client } from '@auth0/auth0-spa-js';
import settings from '../settings';

const client = new Auth0Client({
  domain: settings.auth0.domain,
  client_id: settings.auth0.clientId,
  audience: settings.auth0.audience,
  cacheLocation: settings.auth0.cacheLocation,
});

const fetchBaseQuery = (options: any = {}) => {
  return defaultFetchBaseQuery({
    baseUrl: settings.baseApiUrl,
    prepareHeaders: async function prepareHeaders(headers) {
      const token = await client.getTokenSilently();
      headers.set('authorization', `Bearer ${token}`);
      return headers;
    },
    ...options,
  });
};

// we are supporting the Request object or url string
const fetchWithAuth = async (resource: any, init: any = {}) => {
  const token = await client.getTokenSilently();
  if (typeof resource == 'string') {
    return fetch(resource, {
      ...init,
      headers: {
        ...init.headers,
        Authorization: `Bearer ${token}`,
      },
    });
  } else {
    return fetch({
      ...resource,
      headers: {
        ...init.headers,
        Authorization: `Bearer ${token}`,
      },
    });
  }
};

const { baseApiUrl } = settings;
export { createApi, fetchBaseQuery, fetchWithAuth, client, baseApiUrl };
