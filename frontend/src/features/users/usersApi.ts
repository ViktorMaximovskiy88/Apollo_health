import { createApi, fetchBaseQuery } from '../../app/base-api';
import { ChangeLog } from '../change-log/types';
import { User } from './types';

export const usersApi = createApi({
  reducerPath: 'usersApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['User', 'ChangeLog'],
  endpoints: (builder) => ({
    getUsers: builder.query<User[], void>({
      query: () => '/users/',
      providesTags: (results) => {
        const tags = [{ type: 'User' as const, id: 'LIST' }];
        results?.forEach(({ _id: id }) => tags.push({ type: 'User', id }));
        return tags;
      },
    }),
    getUser: builder.query<User, string | undefined>({
      query: (id) => `/users/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'User' as const, id }],
    }),
    addUser: builder.mutation<User, Partial<User>>({
      query: (body) => ({ url: '/users/', method: 'PUT', body }),
      invalidatesTags: [{ type: 'User', id: 'LIST' }],
    }),
    updateUser: builder.mutation<User, Partial<User>>({
      query: (body) => ({ url: `/users/${body._id}`, method: 'POST', body }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        { type: 'User', id },
        { type: 'ChangeLog', id },
      ],
    }),
    deleteUser: builder.mutation<void, Pick<User, '_id'> & Partial<User>>({
      query: ({ _id: id }) => ({ url: `/users/${id}`, method: 'DELETE' }),
      invalidatesTags: (_r, _e, { _id: id }) => [
        { type: 'User', id },
        { type: 'ChangeLog', id },
      ],
    }),
    getChangeLog: builder.query<ChangeLog[], string>({
      query: (id) => `/change-log/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'ChangeLog', id }],
    }),
  }),
});

export const {
  useGetUserQuery,
  useGetUsersQuery,
  useAddUserMutation,
  useUpdateUserMutation,
  useDeleteUserMutation,
  useGetChangeLogQuery,
} = usersApi;
