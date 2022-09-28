import { LinkOutlined } from '@ant-design/icons';
import { Button } from 'antd';
import { AnchorHTMLAttributes } from 'react';

type ButtonType = 'link' | 'text' | 'default' | 'ghost' | 'primary' | 'dashed' | undefined;

const buttonTypes: ButtonType[] = [
  'link',
  'text',
  'default',
  'ghost',
  'primary',
  'dashed',
  undefined,
];

const buildType = (originalType: any): ButtonType => {
  if (!buttonTypes.includes(originalType)) return;
  return originalType;
};

export function LinkIcon(props: AnchorHTMLAttributes<HTMLAnchorElement>) {
  return (
    <Button
      className="p-0 focus:border focus:border-offset-2 focus:border-blue-500"
      target="_blank"
      rel="noreferrer noopener"
      {...props}
      type={buildType(props.type) ?? 'link'}
    >
      <LinkOutlined className="text-gray-500 hover:text-blue-500 focus:text-blue-500" />
    </Button>
  );
}
