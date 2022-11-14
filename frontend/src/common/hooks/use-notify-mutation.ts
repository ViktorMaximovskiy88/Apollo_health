import { notification } from 'antd';
import { ArgsProps } from 'antd/lib/notification';
import { useEffect } from 'react';

export function useNotifyMutation(
  queryResult: { isSuccess: boolean; isError: boolean },
  successNotificationArgs: Partial<ArgsProps>,
  errorNotificationArgs: Partial<ArgsProps>
) {
  const { isSuccess, isError } = queryResult;
  useEffect(() => {
    if (isSuccess) {
      notification.success({ message: 'Success!', ...successNotificationArgs });
    }
  }, [isSuccess, successNotificationArgs]);
  useEffect(() => {
    if (isError) {
      notification.error({ message: 'Success!', ...errorNotificationArgs });
    }
  }, [isError, errorNotificationArgs]);
}
