import { Button, Popconfirm, Table, Tag } from 'antd';
import { BaseButtonProps } from 'antd/lib/button/button';
import {
  MouseEventHandler,
  AnchorHTMLAttributes,
  ButtonHTMLAttributes,
  RefAttributes,
} from 'react';
import { Link } from 'react-router-dom';
import { ChangeLogModal } from '../change_log/ChangeLogModal';
import { Site } from './types';
import {
  useDeleteSiteMutation,
  useGetChangeLogQuery,
  useGetSitesQuery,
} from './sitesApi';
import { SiteBreadcrumbs } from './SiteBreadcrumbs';

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

function ButtonLink(props: ButtonLinkProps) {
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

export function SitesHomePage() {
  const { data: sites } = useGetSitesQuery();
  const [deleteSite] = useDeleteSiteMutation();
  const formattedSites =
    sites?.filter((u) => !u.disabled).map((u) => ({ ...u, key: u._id })) || [];
  const colors = ['magenta', 'blue', 'green', 'orange', 'purple'];
  const columns = [
    {
      title: 'Name',
      key: 'name',
      render: (site: Site) => {
        return <ButtonLink to={site._id}>{site.name}</ButtonLink>;
      },
    },
    {
      title: 'Tags',
      key: 'tags',
      render: (site: Site) => {
        return site.tags.map((tag) => {
          const simpleHash = tag
            .split('')
            .map((c) => c.charCodeAt(0))
            .reduce((a, b) => a + b);
          const color = colors[simpleHash % colors.length];
          return (
            <Tag color={color} key={tag}>
              {tag}
            </Tag>
          );
        });
      },
    },
    {
      title: 'Actions',
      key: 'action',
      render: (site: Site) => {
        return (
          <>
            <ButtonLink to={`${site._id}/edit`}>Edit</ButtonLink>
            <ChangeLogModal
              target={site}
              useChangeLogQuery={useGetChangeLogQuery}
            />
            <Popconfirm
              title={`Are you sure you want to delete '${site.name}'?`}
              okText="Yes"
              cancelText="No"
              onConfirm={() => deleteSite(site)}
            >
              <ButtonLink danger>Delete</ButtonLink>
            </Popconfirm>
          </>
        );
      },
    },
  ];
  return (
    <div>
      <div className="flex">
        <SiteBreadcrumbs />
        <Link className="ml-auto" to="new">
          <Button>Create Site</Button>
        </Link>
      </div>
      <Table dataSource={formattedSites} columns={columns} />
    </div>
  );
}
