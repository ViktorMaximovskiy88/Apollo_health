import { createApi, fetchBaseQuery } from '../../app/base-api';
import { BaseDocument } from '../../common';

export interface DocumentPipelineTask {
  doc_doc_id: string | undefined;
}

export interface LineageTask {
  site_id: string | undefined;
  reprocess: boolean;
}

export interface EnqueueTask {
  task_type: string;
  payload: DocumentPipelineTask | LineageTask;
}

export interface Task extends BaseDocument {
  task_type: string;
  status: string;
  status_at: string;
  is_complete: boolean;
  completed_at: string;
}

export const taskApi = createApi({
  reducerPath: 'taskApi',
  baseQuery: fetchBaseQuery(),
  tagTypes: ['Task', 'DocumentPipelineTask'],
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
