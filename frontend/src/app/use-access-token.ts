import { useEffect } from 'react';
import { setToken } from './auth0-slice';
import { useAuth0 } from '@auth0/auth0-react';
import { useAppSelector, useAppDispatch } from './store';

export default () => {
  const { isAuthenticated, isLoading, getAccessTokenSilently } = useAuth0();
  const dispatch = useAppDispatch();

  const token = useAppSelector((state: any) => state.auth0.token);

  useEffect(() => {
    if (isAuthenticated && !token) {
      (async (): Promise<void> => {
        const token = await getAccessTokenSilently();
        dispatch(setToken(token));
      })();
    }
  }, [isAuthenticated, token]);

  return token;
};
