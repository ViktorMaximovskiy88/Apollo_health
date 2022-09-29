import { Button, Checkbox, Form, Input, notification, Popconfirm, Select } from 'antd';
import { FormInstance, useForm } from 'antd/lib/form/Form';
import { useCallback, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useInterval } from '../../common/hooks';
import { MainLayout } from '../../components';
import { DocDocumentClassificationPage } from './DocDocumentClassificationPage';
import { ContentExtractionApprovalPage } from '../extractions/ContentExtractionApprovalPage';
import { useGetUsersQuery } from '../users/usersApi';
import { SubmitAction, WorkQueue } from './types';
import {
  useGetWorkQueueQuery,
  useSubmitWorkItemMutation,
  useTakeNextWorkItemMutation,
  useTakeWorkItemMutation,
} from './workQueuesApi';
import { useSelector } from 'react-redux';
import { workQueueTableState } from './workQueueSlice';

function notifyFailedLock() {
  notification.open({
    message: 'Failed to Acquire Lock',
    description:
      'You were unable to acquire the lock for this item. Likely another user is currently editing it.',
  });
}

function workItemPage(
  wq: WorkQueue,
  itemId: string,
  form: FormInstance,
  onSubmit: (u: any) => Promise<void>
) {
  switch (wq.frontend_component) {
    case 'DocDocumentClassificationPage':
      return <DocDocumentClassificationPage docId={itemId} form={form} onSubmit={onSubmit} />;
    case 'ContentExtractionApprovalPage':
      return <ContentExtractionApprovalPage docId={itemId} form={form} onSubmit={onSubmit} />;
  }
}

function WorkQueueActionButton(props: {
  itemId: string;
  action: SubmitAction;
  setAction: (a: SubmitAction) => void;
  setComment: (a: string) => void;
  setReassignment: (a: string) => void;
}) {
  const { data: users } = useGetUsersQuery();
  const [form] = useForm();
  const label = props.action.label;
  const type = props.action.primary ? 'primary' : 'default';

  if (!props.action.require_comment) {
    return (
      <Button onClick={() => props.setAction(props.action)} type={type}>
        {label}
      </Button>
    );
  }

  function onFinish(res: { assignee: string; comment: string }) {
    props.setReassignment(res.assignee);
    props.setComment(res.comment);
    props.setAction(props.action);
  }

  const assignees = users?.map((u) => ({ value: u._id, label: u.full_name }));

  const commentForm = (
    <Form form={form} onFinish={onFinish}>
      <Form.Item name="comment" label="Comment">
        <Input.TextArea />
      </Form.Item>
      <Form.Item name="assignee" label="Assignee">
        <Select options={assignees} />
      </Form.Item>
    </Form>
  );

  return (
    <Popconfirm zIndex={1040} icon={false} title={commentForm} onConfirm={form.submit}>
      <Button type={type}>{label}</Button>
    </Popconfirm>
  );
}

function WorkItemSubmitBar(props: {
  itemId: string;
  readonly: boolean;
  wq: WorkQueue;
  takeNext: boolean;
  setTakeNext: (tn: boolean) => void;
  setAction: (a: SubmitAction) => void;
  setReassignment: (a: string) => void;
  setComment: (a: string) => void;
}) {
  const navigate = useNavigate();

  if (props.readonly) return null;

  return (
    <div className="flex space-x-2 items-center">
      {props.wq.submit_actions.map((action) => (
        <WorkQueueActionButton
          itemId={props.itemId}
          key={props.itemId + action.label}
          action={action}
          setAction={props.setAction}
          setComment={props.setComment}
          setReassignment={props.setReassignment}
        />
      ))}
      <Button onClick={() => navigate('../../..')}>Cancel</Button>
      <span>Auto Take</span>
      <Checkbox checked={props.takeNext} onChange={(e) => props.setTakeNext(e.target.checked)} />
    </div>
  );
}

export function WorkQueueWorkItem(props: { wq: WorkQueue; itemId: string; readonly: boolean }) {
  const [form] = useForm();
  const [action, setAction] = useState<SubmitAction>();
  const [takeNext, setTakeNext] = useState(true);
  const [reassignment, setReassignment] = useState<string>();
  const [comment, setComment] = useState<string>();
  const navigate = useNavigate();
  const [submitWorkItem] = useSubmitWorkItemMutation();
  const [takeNextWorkItem] = useTakeNextWorkItemMutation();
  const tableState = useSelector(workQueueTableState);

  useEffect(() => {
    if (action) {
      form.submit();
      setAction(undefined);
    }
  }, [action, form]);

  const onSubmit = useCallback(
    async (item: any) => {
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
      await submitWorkItem({ itemId: props.itemId, workQueueId: props.wq._id, body });
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
          itemId={props.itemId}
          readonly={props.readonly}
          wq={props.wq}
          setAction={setAction}
          takeNext={takeNext}
          setTakeNext={setTakeNext}
          setComment={setComment}
          setReassignment={setReassignment}
        />
      }
    >
      {workItemPage(props.wq, props.itemId, form, onSubmit)}
    </MainLayout>
  );
}

export function ProcessWorkItemPage() {
  const params = useParams();
  const navigate = useNavigate();
  const itemId = params.itemId;
  const workQueueId = params.queueId;
  const [takeWorkItem] = useTakeWorkItemMutation();
  const { data: wq } = useGetWorkQueueQuery(workQueueId);
  const { watermark } = useInterval(5000);

  useEffect(() => {
    (async () => {
      const response = await takeWorkItem({ itemId, workQueueId });
      if ('error' in response || !response.data.acquired_lock) {
        navigate(-1);
        notifyFailedLock();
      }
    })();
  }, [watermark, itemId, workQueueId, navigate, takeWorkItem]);

  if (!wq || !itemId) return null;

  return <WorkQueueWorkItem wq={wq} itemId={itemId} readonly={false} />;
}

export function ReadonlyWorkItemPage() {
  const params = useParams();
  const workQueueId = params.queueId;
  const itemId = params.itemId;
  const { data: wq } = useGetWorkQueueQuery(workQueueId);
  if (!wq || !itemId) return null;

  return <WorkQueueWorkItem wq={wq} itemId={itemId} readonly />;
}
