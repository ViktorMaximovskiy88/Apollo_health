import Title from 'antd/lib/typography/Title';
import { useNavigate } from 'react-router-dom';
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
    <div>
      <div className="flex">
        <Title level={4}>Create User</Title>
      </div>
      <UserForm onFinish={tryAddUser} />
    </div>
  );
}
