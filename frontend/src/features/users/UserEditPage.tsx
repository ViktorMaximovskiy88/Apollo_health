import Title from 'antd/lib/typography/Title';
import { useNavigate, useParams } from 'react-router-dom';
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
    <div>
      <div className="flex">
        <Title level={4}>Edit User</Title>
      </div>
      <UserForm onFinish={tryUpdateUser} initialValues={user} />
    </div>
  );
}
