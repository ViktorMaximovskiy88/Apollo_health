import { useParams, useNavigate } from 'react-router-dom';
import { Viewer, Worker } from '@react-pdf-viewer/core';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';

import '@react-pdf-viewer/core/lib/styles/index.css';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';
import Title from 'antd/lib/typography/Title';
import { useGetDocumentAssessmentQuery, useTakeDocumentAssessmentMutation } from './assessmentsApi';
import { AssessmentForm } from './AssessmentForm';
import { useEffect } from 'react';
import { notification } from 'antd';
import { useGetDocumentQuery } from '../documents/documentsApi';
import { useGetWorkQueueQuery } from '../work_queue/workQueuesApi';

export function DocumentAssessmentPage(props: { readonly: boolean | undefined }) {
  const assessmentId = useParams().assessmentId;
  const workQueueId = useParams().queueId;
  const { data: assessment } = useGetDocumentAssessmentQuery(assessmentId);
  const { data: workQueue } = useGetWorkQueueQuery(workQueueId);
  const { data: document } = useGetDocumentQuery(assessment?.retrieved_document_id, { skip: !assessment });

  const defaultLayoutPluginInstance = defaultLayoutPlugin();
  if (!assessment || !document || !workQueue) return null;
  const docId = assessment.retrieved_document_id;

  return (
    <div className="flex flex-col h-full overflow-auto">
      <Title level={4}>{assessment.name}</Title>
      <div className="flex space-x-4 overflow-auto flex-grow">
        <div className="w-1/2 h-full overflow-auto">
          <AssessmentForm readonly={props.readonly} assessment={assessment} document={document} workQueue={workQueue}/>
        </div>
        <Worker workerUrl="/pdf.worker.min.js">
          <div className="w-1/2 h-full overflow-auto ant-tabs-pdf-viewer">
            <Viewer
              fileUrl={`/api/v1/documents/${docId}.pdf`}
              plugins={[defaultLayoutPluginInstance]}
            />
          </div>
        </Worker>
      </div>
    </div>
  );
}

function notifyFailedLock() {
  notification.open({
    message: 'Failed to Acquire Lock',
    description: 'You were unable to acquire the lock for this assessment. Likely another user is currently editing it.',
  })
}

export function ProcessDocumentAssessmentPage() {
  const params = useParams();
  const navigate = useNavigate();
  const assessmentId = params.assessmentId;
  const workQueueId = params.queueId;
  const [takeDocumentAssessment, { data: response }] = useTakeDocumentAssessmentMutation();

  useEffect(() => {
    (async () => {
      const response = await takeDocumentAssessment({ assessmentId, workQueueId });
      if ('error' in response || !response.data.acquired_lock) {
        navigate(-1)
        notifyFailedLock()
      }
    })()
  }, [assessmentId, workQueueId])
  
  if (!response) return null;
  
  return (
    <div className="h-full p-4">
      <DocumentAssessmentPage readonly={false}/>
    </div>
  );
}
export function ReadonlyDocumentAssessmentPage() {
  return (
    <div className="h-full p-4">
      <DocumentAssessmentPage readonly/>
    </div>
  );
}