import { createApi, fetchBaseQuery } from './base-api';
import { BaseDocument } from '../common';

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
  tagTypes: ['Task'],
  endpoints: (builder) => ({
    getTask: builder.query<Task, string | undefined>({
      query: (taskId) => `/task/${taskId}`,
      providesTags: (_r, _e, id) => [{ type: 'Task' as const, id }],
      async onCacheEntryAdded(arg, { updateCachedData, cacheDataLoaded, cacheEntryRemoved }) {
        // once loaded will setup polling here per taskId
        // caveat, this doesnt qork with useLazy... need to figure if we can make that happen
        // otherwise its more bother than its worth
        console.log(arg, updateCachedData, cacheDataLoaded, cacheEntryRemoved);
      },
    }),
  }),
});

export const { useLazyGetTaskQuery } = taskApi;
