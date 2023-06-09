import { useEffect, useState } from 'react';
import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../../app/store';
import { useSelector, useDispatch } from 'react-redux';
import { makeActionDispatch } from '../../common/helpers';
import { notification } from 'antd';
import { uniqBy } from 'lodash';
import { useLazyGetTaskQuery, useEnqueueTaskMutation } from './taskApi';
import { Task } from './types';
import { useInterval } from '../../common/hooks';

interface TaskState {
  pending: Task[];
}

export const taskSlice = createSlice({
  name: 'task',
  initialState: {
    pending: [],
  } as TaskState,
  reducers: {
    setPendingTask: (state, action: PayloadAction<Task>) => {
      state.pending = uniqBy([...state.pending, action.payload], '_id');
    },
  },
});

export const taskSelector = createSelector(
  (state: RootState) => state.task,
  (taskState) => taskState
);

export function useTaskSlice() {
  const state = useSelector(taskSelector);
  const dispatch = useDispatch();
  return {
    state: state as TaskState,
    actions: makeActionDispatch(taskSlice.actions, dispatch),
  };
}

export const { reducer } = taskSlice;
export default taskSlice;

export function useTaskWorker(successFunc: Function = () => {}) {
  const [getTask] = useLazyGetTaskQuery();
  const [enqueueTask] = useEnqueueTaskMutation();

  const { watermark, setActive, isActive } = useInterval(5000, { active: false });
  const [task, setTask] = useState<Task | undefined>(undefined);

  useEffect(() => {
    (async () => {
      if (task && isActive && watermark) {
        const { data } = await getTask(task._id);
        if (data?.is_complete && data.status === 'FINISHED') {
          notification.success({
            message: `${data?.task_type}: ${data?.status}`,
          });
          setActive(false);
          successFunc(data);
        } else if (data?.is_complete && data.status === 'FAILED') {
          notification.error({
            message: `${data?.task_type}: ${data?.status}`,
          });
          setActive(false);
        }
      }
    })();
  }, [watermark, isActive, task]);

  return async (task_type: string, payload: any) => {
    const task = await enqueueTask({ task_type, payload }).unwrap();
    if (task) {
      notification.success({
        message: `${task.task_type}: ${task.status}`,
      });
      setTask(task);
      setActive(true);
    } else {
      successFunc(task);
    }
  };
}
