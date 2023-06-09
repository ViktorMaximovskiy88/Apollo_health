import { useAuth0 } from '@auth0/auth0-react';
import { useGetUsersQuery } from '../../features/users/usersApi';
import { User } from '../../features/users/types';

export const useCurrentUser = (): User | undefined => {
  const { user: auth0User } = useAuth0();
  const { data: users } = useGetUsersQuery();
  const currentUser: User | undefined = users?.find((user) => user.email === auth0User?.email);
  return currentUser;
};
