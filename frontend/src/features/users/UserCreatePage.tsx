import { useNavigate } from 'react-router-dom';
import { MainLayout } from '../../components';
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
    <MainLayout>
      <UserForm onFinish={tryAddUser} />
    </MainLayout>
  );
}
