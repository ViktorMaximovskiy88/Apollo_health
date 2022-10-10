import {
  BaseQueryFn,
  FetchArgs,
  FetchBaseQueryError,
  FetchBaseQueryMeta,
  QueryDefinition,
} from '@reduxjs/toolkit/dist/query';
import { UseQuery } from '@reduxjs/toolkit/dist/query/react/buildHooks';
import { Button, Modal, Table } from 'antd';
import { prettyDateTimeFromISO } from '../../common';
import { useState } from 'react';
import { useGetUsersQuery } from '../users/usersApi';
import { ChangeLog, Patch } from './types';
import { User } from '../users/types';

function prettyOp(op: string) {
  if (op === 'replace') {
    return 'Replace';
  } else if (op === 'add') {
    return 'Add';
  } else if (op === 'remove') {
    return 'Remove';
  } else if (op === 'move') {
    return 'Move';
  } else {
    return 'Other';
  }
}

function prettyPath(path: string) {
  return path;
}

function prettyUser(user?: User) {
  if (!user) {
    return 'Unassigned';
  }
  return `${user.full_name}`;
}

function prettyReassignment(op: Patch, users?: User[]) {
  if (!users) return '';
  const prevAssignee = users.find((user) => user._id === op.prev);
  const currentAssignee = users.find((user) => user._id === op.value);
  return `${prettyUser(prevAssignee)} -> ${prettyUser(currentAssignee)}`;
}

function prettyValue(op: Patch) {
  if (op.prev) {
    return `${op.prev?.toString()} -> ${op.value?.toString()}`;
  } else if (op.from) {
    return op.from?.toString();
  } else {
    return op.value?.toString();
  }
}

export function ChangeLogDeltaTable(props: { log: ChangeLog; users?: User[] }) {
  return (
    <table>
      <thead>
        <tr>
          <th>Operation</th>
          <th>Field</th>
          <th>Value</th>
        </tr>
      </thead>
      <tbody>
        {props.log.delta?.map((op) => {
          return (
            <tr key={JSON.stringify(op)}>
              <td>{prettyOp(op.op)}</td>
              <td>{prettyPath(op.path)}</td>
              {op.path === '/assignee' ? (
                <td>{prettyReassignment(op, props?.users)}</td>
              ) : (
                <td>{prettyValue(op)}</td>
              )}
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

type ChangeLogUseQuery = UseQuery<
  QueryDefinition<
    string,
    BaseQueryFn<string | FetchArgs, unknown, FetchBaseQueryError, {}, FetchBaseQueryMeta>,
    'ChangeLog',
    ChangeLog[]
  >
>;
/*
(
    UseQuerySubscriptionOptions &
    UseQueryStateOptions<
        QueryDefinition<
            string,
            BaseQueryFn<string | FetchArgs, unknown, FetchBaseQueryError, {}, FetchBaseQueryMeta>,
            "User" | "ChangeLog",
            ChangeLog[],
            "usersApi"
        >,
        UseQueryStateDefaultResult<...>
    >
)
*/
export function ChangeLogModal(props: {
  target: { _id: string };
  useChangeLogQuery: ChangeLogUseQuery;
}) {
  const [open, setopen] = useState(false);
  function openModal() {
    setopen(true);
  }
  function closeModal() {
    setopen(false);
  }
  const columns = [
    {
      title: 'Actions',
      key: 'action',
      render: (log: ChangeLog) => {
        const lookup: any = {
          CREATE: 'Created',
          UPDATE: 'Updated',
          DELETE: 'Deleted',
        };
        return <>{lookup[log.action]}</>;
      },
    },
    {
      title: 'User',
      key: 'user',
      render: (log: ChangeLog) => {
        const user = users?.find((u) => u._id === log.user_id);
        return <>{user?.full_name}</>;
      },
    },
    {
      title: 'Time',
      key: 'time',
      render: (log: ChangeLog) => {
        return prettyDateTimeFromISO(log.time);
      },
    },
  ];
  const { data: changeLogs } = props.useChangeLogQuery(props.target._id, {
    skip: !open,
  });
  const formattedLogs = changeLogs?.map((log: ChangeLog) => ({
    ...log,
    key: log._id,
  }));
  const { data: users } = useGetUsersQuery();
  return (
    <>
      <Button type="link" size="small" onClick={openModal}>
        Log
      </Button>
      <Modal
        title="Change Log"
        open={open}
        onCancel={closeModal}
        width={1000}
        footer={[
          <Button key="submit" type="primary" onClick={closeModal}>
            Ok
          </Button>,
        ]}
      >
        <Table
          dataSource={formattedLogs}
          columns={columns}
          expandable={{
            expandedRowRender: (log) => <ChangeLogDeltaTable log={log} users={users} />,
            rowExpandable: (log) => !!log.delta,
          }}
        />
      </Modal>
    </>
  );
}
