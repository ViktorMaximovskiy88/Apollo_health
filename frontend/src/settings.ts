
interface Auth0Config {
  domain: string;
  clientId: string;
  audience: string;
  cacheLocation: any;
}

interface Settings {
  baseApiUrl: string;
  auth0: Auth0Config;
}

const auth0Settings: Auth0Config = {
  domain: process.env.REACT_APP_AUTH0_DOMAIN as string,
  clientId: process.env.REACT_APP_AUTH0_CLIENT_ID as string,
  audience: process.env.REACT_APP_AUTH0_AUDIENCE as string,
  cacheLocation: 'localstorage',
};

const settings: Settings = {
  baseApiUrl: '/api/v1',
  auth0: auth0Settings,
};

export default settings;
