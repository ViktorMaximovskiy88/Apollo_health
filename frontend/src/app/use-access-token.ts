import { useMemo, useState } from 'react';
import { useAuth0 } from '@auth0/auth0-react';

export default () => {
  const { isAuthenticated, getAccessTokenSilently } = useAuth0();
  const [token, setToken] = useState("");

  useMemo(() => {
    if (isAuthenticated && !token) {
      let _token = "";
      (async (): Promise<void> => {
        _token = await getAccessTokenSilently();
        setToken(_token);
      })();
    }
  }, [isAuthenticated, token]);
  
  return token;
};
