// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import '@testing-library/jest-dom/extend-expect';

// silences console warning: "async-validator: [ '${label} is required!' ]"
import Schema from 'async-validator';
Schema.warning = function () {};

jest.mock('@auth0/auth0-spa-js', () => {
  return {
    Auth0Client: jest.fn().mockImplementation(() => {
      return { getTokenSilently: jest.fn() };
    }),
  };
});
