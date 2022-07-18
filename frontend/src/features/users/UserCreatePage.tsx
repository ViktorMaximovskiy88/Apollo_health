import { Layout } from 'antd';
import Title from 'antd/lib/typography/Title';
import { useNavigate } from 'react-router-dom';
import { PageHeader, PageLayout } from '../../components';
import { User } from './types';
import { UserForm } from './UserForm';
import { useAddUserMutation } from './usersApi';

export function UserCreatePage() {
  const [addUser] = useAddUserMutation();
  const navigate = useNavigate();

  async function tryAddUser(user: Partial<User>) {
    await addUser(user);
    navigate('/users');
  }

  return (
    <PageLayout>
      <PageHeader header={'Create User'} />
      <UserForm onFinish={tryAddUser} />
    </PageLayout>
  );
}
