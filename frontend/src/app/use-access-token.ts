import { useMemo, useState } from 'react';
import { useAuth0 } from '@auth0/auth0-react';

export default () => {
  const { isAuthenticated, getAccessTokenSilently } = useAuth0();
  const [token, setToken] = useState("");

  useMemo(() => {
    if (isAuthenticated && !token) {
      (async (): Promise<void> => {
        const token = await getAccessTokenSilently();
        setToken(token);
      })();
    }
  }, [isAuthenticated, token]);

  console.log(token, 'first')
  return token;
};
