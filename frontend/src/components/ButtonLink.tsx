import { Button } from 'antd';
import { BaseButtonProps } from 'antd/lib/button/button';
import {
  AnchorHTMLAttributes,
  ButtonHTMLAttributes,
  MouseEventHandler,
  RefAttributes,
} from 'react';
import { Link } from 'react-router-dom';

type ButtonLinkProps = { to?: string } & JSX.IntrinsicAttributes &
  Partial<
    {
      href: string;
      target?: string | undefined;
      onClick?: MouseEventHandler<HTMLElement> | undefined;
    } & BaseButtonProps &
      Omit<AnchorHTMLAttributes<any>, 'type' | 'onClick'> & {
        htmlType?: 'button' | 'submit' | 'reset' | undefined;
        onClick?: MouseEventHandler<HTMLElement> | undefined;
      } & Omit<ButtonHTMLAttributes<any>, 'type' | 'onClick'>
  > &
  RefAttributes<HTMLElement>;

export function ButtonLink(props: ButtonLinkProps) {
  const { children, to, ...otherProps } = props;
  if (to) {
    return (
      <Link to={to}>
        <Button type="link" size="small" {...otherProps}>
          {children}
        </Button>
      </Link>
    );
  } else {
    return (
      <Button type="link" size="small" {...otherProps}>
        {children}
      </Button>
    );
  }
}
