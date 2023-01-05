import { LinkOutlined } from '@ant-design/icons';
import { AnchorButtonProps, NativeButtonProps } from 'antd/lib/button/button';

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

export function LinkIcon(props: Partial<AnchorButtonProps & NativeButtonProps>) {
  return (
    <a
      className="p-0 focus:border focus:border-offset-2 focus:border-blue-500"
      target="_blank"
      rel="noreferrer noopener"
      {...props}
      type={buildType(props.type) ?? 'link'}
    >
      <LinkOutlined className="text-gray-500 hover:text-blue-500 focus:text-blue-500" />
    </a>
  );
}
