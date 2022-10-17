import { createApi, fetchBaseQuery } from '../../app/base-api';
import { Comment } from './types';

export const commentsApi = createApi({
  reducerPath: 'commentsApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['Comment', 'ChangeLog'],
  endpoints: (builder) => ({
    getComments: builder.query<{ data: Comment[]; total: number }, string | undefined>({
      query: (targetId) => {
        const sorts = [
          {
            name: 'time',
            dir: 1,
          },
        ];
        const filterValue = [
          {
            name: 'target_id',
            operator: 'eq',
            type: 'string',
            value: targetId,
          },
        ];
        const args = [
          `sorts=${encodeURIComponent(JSON.stringify(sorts))}`,
          `filters=${encodeURIComponent(JSON.stringify(filterValue))}`,
        ];
        return `/comments/?${args.join('&')}`;
      },
      providesTags: (_r, _e, targetId) => {
        return [{ type: 'Comment' as const, id: targetId }];
      },
    }),
    getComment: builder.query<Comment, string | undefined>({
      query: (id) => `/comments/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'Comment' as const, id }],
    }),
    addComment: builder.mutation<Comment, Partial<Comment>>({
      query: (body) => ({ url: '/comments/', method: 'PUT', body }),
      invalidatesTags: (r) => [{ type: 'Comment', id: r?.target_id }],
    }),
    updateComment: builder.mutation<Comment, Partial<Comment>>({
      query: (body) => ({ url: `/comments/${body._id}`, method: 'POST', body }),
      invalidatesTags: (_r, _e, { _id: id, target_id }) => [
        { type: 'Comment', id },
        { type: 'Comment', id: target_id },
      ],
    }),
    deleteComment: builder.mutation<void, Pick<Comment, '_id'> & Partial<Comment>>({
      query: ({ _id: id }) => ({ url: `/comments/${id}`, method: 'DELETE' }),
      invalidatesTags: (_r, _e, { _id: id, target_id }) => [
        { type: 'Comment', id },
        { type: 'Comment', id: target_id },
      ],
    }),
  }),
});

export const {
  useGetCommentQuery,
  useGetCommentsQuery,
  useAddCommentMutation,
  useUpdateCommentMutation,
  useDeleteCommentMutation,
} = commentsApi;
