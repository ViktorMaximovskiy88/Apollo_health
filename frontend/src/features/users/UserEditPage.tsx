import { useNavigate, useParams } from 'react-router-dom';
import { MainLayout } from '../../components';
import { User } from './types';
import { UserForm } from './UserForm';
import { useGetUserQuery, useUpdateUserMutation } from './usersApi';

export function UserEditPage() {
  const params = useParams();
  const { data: user } = useGetUserQuery(params.userId);
  const [updateUser] = useUpdateUserMutation();
  const navigate = useNavigate();
  if (!user) return null;

  async function tryUpdateUser(user: Partial<User>) {
    user._id = params.userId;
    await updateUser(user);
    navigate('/users');
  }
  return (
    <MainLayout>
      <UserForm onFinish={tryUpdateUser} initialValues={user} />
    </MainLayout>
  );
}
