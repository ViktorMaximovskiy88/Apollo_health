import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { ChangeLog } from '../change_log/types';
import { NestedPartial } from '../types';
import { DocumentAssessment, TakeDocumentAssessmentResponse } from './types';

export const assessmentsApi = createApi({
  reducerPath: 'assessmentsApi',
  baseQuery: fetchBaseQuery({ baseUrl: '/api/v1/' }),
  tagTypes: ['DocumentAssessment', 'ChangeLog'],
  endpoints: (builder) => ({
    getWorkQueueAssessments: builder.query<DocumentAssessment[], string | undefined>({
      query: (id) => `/assessments/?work_queue_id=${id}`,
      providesTags: (results, _e, id) => {
        const tags = [{ type: 'DocumentAssessment' as const, id: id }];
        results?.forEach(({ _id: id }) => tags.push({ type: 'DocumentAssessment', id }));
        return tags;
      },
    }),
    takeDocumentAssessment: builder.mutation<TakeDocumentAssessmentResponse, { assessmentId?: string, workQueueId?: string }>({
      query: ({assessmentId, workQueueId}) => ({
        url: `/assessments/${assessmentId}/take?work_queue_id=${workQueueId}`,
        method: 'POST',
      })
    }),
    getDocumentAssessment: builder.query<DocumentAssessment, string | undefined>({
      query: (id) => `/assessments/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'DocumentAssessment' as const, id }],
    }),
    updateDocumentAssessment: builder.mutation<DocumentAssessment, NestedPartial<DocumentAssessment>>({
      query: (body) => ({ url: `/assessments/${body._id}`, method: 'POST', body }),
      invalidatesTags: (_r, _e, { _id: id }) => ([
        { type: 'DocumentAssessment', id: 'LIST' },
        { type: 'DocumentAssessment', id }
      ]),
    }),
    getChangeLog: builder.query<ChangeLog[], string>({
      query: (id) => `/change-log/${id}`,
      providesTags: (_r, _e, id) => [{ type: 'ChangeLog', id }],
    }),
  }),
});

export const {
  useGetWorkQueueAssessmentsQuery,
  useTakeDocumentAssessmentMutation,
  useGetDocumentAssessmentQuery,
  useUpdateDocumentAssessmentMutation,
  useGetChangeLogQuery,
} = assessmentsApi;
