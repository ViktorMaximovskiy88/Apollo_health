import { notification } from 'antd';

type NotificationType = 'success' | 'info' | 'warning' | 'error';

export const Notification = (type: NotificationType, title: string, description: string) => {
  notification[type]({
    message: title,
    description,
  });
};
