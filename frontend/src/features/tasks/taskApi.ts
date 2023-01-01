import { createApi, fetchBaseQuery } from '../../app/base-api';
import { Task, EnqueueTask } from './types';

export const taskApi = createApi({
  reducerPath: 'taskApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['Task', 'DocumentPipelineTask', 'SiteDocsPipelineTask'],
  endpoints: (builder) => ({
    getTask: builder.query<Task, string | undefined>({
      query: (taskId) => `/task/${taskId}`,
      providesTags: (_r, _e, id) => [{ type: 'Task' as const, id }],
    }),
    enqueueTask: builder.mutation<Task, EnqueueTask>({
      query: (body) => ({
        url: `/task/enqueue/${body.task_type}`,
        method: 'POST',
        body: body.payload,
      }),
    }),
  }),
});

export const { useLazyGetTaskQuery, useEnqueueTaskMutation } = taskApi;
