import { Layout, Button, Popconfirm, Table, Tag } from 'antd';
import Title from 'antd/lib/typography/Title';
import { Link } from 'react-router-dom';
import { ButtonLink } from '../../components/ButtonLink';
import { ChangeLogModal } from '../change_log/ChangeLogModal';
import { User } from './types';
import {
  useDeleteUserMutation,
  useGetChangeLogQuery,
  useGetUsersQuery,
} from './usersApi';

export function UsersHomePage() {
  const { data: users } = useGetUsersQuery();
  const [deleteUser] = useDeleteUserMutation();
  const formattedUsers =
    users?.filter((u) => !u.disabled).map((u) => ({ ...u, key: u._id })) || [];
  const colors = ['magenta', 'blue', 'green', 'orange', 'purple'];
  const columns = [
    {
      title: 'Name',
      key: 'name',
      render: (user: User) => {
        return <ButtonLink to={`${user._id}/edit`}>{user.full_name}</ButtonLink>;
      },
    },
    { title: 'Email', key: 'email', dataIndex: 'email' },
    {
      title: 'Roles',
      key: 'roles',
      render: (user: User) => {
        return user.roles.map((role) => {
          const simpleHash = role
            .split('')
            .map((c) => c.charCodeAt(0))
            .reduce((a, b) => a + b);
          const color = colors[simpleHash % colors.length];
          return (
            <Tag color={color} key={role}>
              {role}
            </Tag>
          );
        });
      },
    },
    {
      title: 'Actions',
      key: 'action',
      render: (user: User) => {
        return (
          <>
            <ChangeLogModal
              target={user}
              useChangeLogQuery={useGetChangeLogQuery}
            />
            <Popconfirm
              title={`Are you sure you want to delete '${user.full_name}'?`}
              okText="Yes"
              cancelText="No"
              onConfirm={() => deleteUser(user)}
            >
              <ButtonLink danger>Delete</ButtonLink>
            </Popconfirm>
          </>
        );
      },
    },
  ];
  return (
    <Layout className="bg-transparent p-4">
      <div className="flex">
        <Title className="inline-block" level={4}>
          Users
        </Title>
        <Link className="ml-auto" to="new">
          <Button>Create User</Button>
        </Link>
      </div>
      <Table dataSource={formattedUsers} columns={columns} />
    </Layout>
  );
}
