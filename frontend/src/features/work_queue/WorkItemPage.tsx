import { Button, Checkbox, Form, Input, notification, Popconfirm } from 'antd';
import { FormInstance, useForm } from 'antd/lib/form/Form';
import { useCallback, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useInterval } from '../../common/hooks';
import { MainLayout } from '../../components';
import { DocDocumentClassificationPage } from './DocDocumentClassificationPage';
import { ContentExtractionApprovalPage } from '../extractions/ContentExtractionApprovalPage';
import { SubmitAction, WorkQueue } from './types';
import { useGetWorkQueueQuery } from './workQueuesApi';
import { useSelector } from 'react-redux';
import { workQueueTableState } from './workQueueSlice';
import {
  useSubmitWorkItemMutation,
  useTakeNextWorkItemMutation,
  useTakeWorkItemMutation,
} from '../doc_documents/docDocumentApi';
import { Assignee } from '../sites/form/AssigneeInput';

function notifyFailedLock() {
  notification.open({
    message: 'Failed to Acquire Lock',
    description:
      'You were unable to acquire the lock for this item. Likely another user is currently editing it.',
  });
}

function workItemPage(
  wq: WorkQueue,
  docDocumentId: string,
  form: FormInstance,
  onSubmit: (u: any) => Promise<void>
) {
  switch (wq.frontend_component) {
    case 'DocDocumentClassificationPage':
      return (
        <DocDocumentClassificationPage docId={docDocumentId} form={form} onSubmit={onSubmit} />
      );
    case 'ContentExtractionApprovalPage':
      return (
        <ContentExtractionApprovalPage docId={docDocumentId} form={form} onSubmit={onSubmit} />
      );
  }
}

function WorkQueueActionButton(props: {
  docDocumentId: string;
  action: SubmitAction;
  setAction: (a: SubmitAction) => void;
  setComment: (a: string) => void;
  setReassignment: (a: string) => void;
  loading: boolean;
}) {
  const [form] = useForm();
  const label = props.action.label;
  const type = props.action.primary ? 'primary' : 'default';

  if (!props.action.require_comment) {
    return (
      <Button
        onClick={() => {
          props.setAction(props.action);
        }}
        type={type}
        loading={props.loading}
      >
        {label}
      </Button>
    );
  }

  function onFinish(res: { assignee: string; comment: string }) {
    props.setReassignment(res.assignee);
    props.setComment(res.comment);
    props.setAction(props.action);
  }

  const commentForm = (
    <Form form={form} onFinish={onFinish}>
      <Form.Item name="comment" label="Comment">
        <Input.TextArea />
      </Form.Item>
      <Assignee />
    </Form>
  );

  return (
    <Popconfirm zIndex={1040} icon={false} title={commentForm} onConfirm={form.submit}>
      <Button type={type}>{label}</Button>
    </Popconfirm>
  );
}

function WorkItemSubmitBar(props: {
  docDocumentId: string;
  readonly: boolean;
  wq: WorkQueue;
  takeNext: boolean;
  setTakeNext: (tn: boolean) => void;
  setAction: (a: SubmitAction) => void;
  setReassignment: (a: string) => void;
  setComment: (a: string) => void;
  loading: boolean;
}) {
  const navigate = useNavigate();

  if (props.readonly) return null;

  return (
    <div className="flex space-x-2 items-center">
      <Button onClick={() => navigate('../..')}>Cancel</Button>
      {props.wq.submit_actions.map((action) => (
        <WorkQueueActionButton
          docDocumentId={props.docDocumentId}
          key={props.docDocumentId + action.label}
          action={action}
          setAction={props.setAction}
          setComment={props.setComment}
          setReassignment={props.setReassignment}
          loading={props.loading}
        />
      ))}
      <span>Auto Take</span>
      <Checkbox checked={props.takeNext} onChange={(e) => props.setTakeNext(e.target.checked)} />
    </div>
  );
}

const useOnActionChangeSubmitForm = (form: FormInstance) => {
  const [action, setAction] = useState<SubmitAction>();

  useEffect(() => {
    if (action) {
      form
        .validateFields()
        .then(() => {
          form.submit();
        })
        .catch((e) => {
          console.log(`Validation failed. Validation errors: ${e}`);
        });
      setAction(undefined);
    }
  }, [action, form, setAction]);

  return { action, setAction };
};

export function WorkQueueWorkItem(props: {
  wq: WorkQueue;
  docDocumentId: string;
  readonly: boolean;
}) {
  const [form] = useForm();
  const { action, setAction } = useOnActionChangeSubmitForm(form);

  const [takeNext, setTakeNext] = useState(true);
  const [reassignment, setReassignment] = useState<string>();
  const [comment, setComment] = useState<string>();
  const navigate = useNavigate();
  const [submitWorkItem] = useSubmitWorkItemMutation();
  const [takeNextWorkItem] = useTakeNextWorkItemMutation();
  const tableState = useSelector(workQueueTableState);
  const [loading, setLoading] = useState(false);

  const onSubmit = useCallback(
    async (item: any) => {
      setLoading(true);
      const defaultAction = props.wq.submit_actions.find((a) => a.primary);
      const chosenAction = action ? action : defaultAction;
      const updates = {
        ...item,
        ...chosenAction?.submit_action,
      };
      const body = {
        action_label: chosenAction?.label,
        comment,
        reassignment,
        updates,
      };
      await submitWorkItem({ docDocumentId: props.docDocumentId, workQueueId: props.wq._id, body });
      if (takeNext) {
        const response = await takeNextWorkItem({ queueId: props.wq._id, tableState });
        if ('data' in response) {
          if (!response.data.acquired_lock) {
            notification.success({
              message: 'Queue Empty',
              description: 'Congratulations! This queue has been emptied.',
            });
            navigate('../../..');
          } else {
            navigate(`../../${response.data.item_id}/process`);
          }
        }
        setLoading(false);
      } else {
        navigate('../../..');
      }
    },
    [
      props,
      action,
      takeNext,
      navigate,
      tableState,
      reassignment,
      comment,
      submitWorkItem,
      takeNextWorkItem,
    ]
  );

  return (
    <MainLayout
      sectionToolbar={
        <WorkItemSubmitBar
          docDocumentId={props.docDocumentId}
          readonly={props.readonly}
          wq={props.wq}
          setAction={setAction}
          takeNext={takeNext}
          setTakeNext={setTakeNext}
          setComment={setComment}
          setReassignment={setReassignment}
          loading={loading}
        />
      }
    >
      {workItemPage(props.wq, props.docDocumentId, form, onSubmit)}
    </MainLayout>
  );
}

export function ProcessWorkItemPage() {
  const params = useParams();
  const navigate = useNavigate();
  const docDocumentId = params.docDocumentId;
  const workQueueId = params.queueId;
  const [takeWorkItem] = useTakeWorkItemMutation();
  const { data: wq } = useGetWorkQueueQuery(workQueueId);
  const { watermark } = useInterval(5000, { background: true });

  useEffect(() => {
    (async () => {
      const response = await takeWorkItem({ docDocumentId, workQueueId });
      if ('error' in response || !response.data.acquired_lock) {
        navigate(-1);
        notifyFailedLock();
      }
    })();
  }, [watermark, docDocumentId, workQueueId, navigate, takeWorkItem]);

  if (!wq || !docDocumentId) return null;

  return <WorkQueueWorkItem wq={wq} docDocumentId={docDocumentId} readonly={false} />;
}

export function ReadonlyWorkItemPage() {
  const params = useParams();
  const workQueueId = params.queueId;
  const docDocumentId = params.docDocumentId;
  const { data: wq } = useGetWorkQueueQuery(workQueueId);
  if (!wq || !docDocumentId) return null;

  return <WorkQueueWorkItem wq={wq} docDocumentId={docDocumentId} readonly />;
}
