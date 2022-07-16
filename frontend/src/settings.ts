export interface Auth0Config {
  domain: string;
  clientId: string;
  audience: string;
  cacheLocation: any;
  redirectUri: string;
}

export interface Settings {
  baseApiUrl: string;
  auth0: Auth0Config;
}

const auth0Settings: Auth0Config = {
  domain: process.env.REACT_APP_AUTH0_DOMAIN as string,
  clientId: process.env.REACT_APP_AUTH0_CLIENT_ID as string,
  audience: process.env.REACT_APP_AUTH0_AUDIENCE as string,
  cacheLocation: 'localstorage',
  redirectUri: window.location.origin as string,
};

const settings: Settings = {
  baseApiUrl: process.env.REACT_APP_BASE_API_URL as string,
  auth0: auth0Settings,
};

export default settings;
