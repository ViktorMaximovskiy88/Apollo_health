import { useMemo, useState } from 'react';
import { Form, Select } from 'antd';
import { User } from '../users/types';
import { useGetUsersQuery } from '../users/usersApi';

const { Option } = Select;

interface OptionType {
  label: string;
  value: string | null;
}
const useOptions = (): OptionType[] => {
  const { data: users } = useGetUsersQuery();
  return useMemo(() => {
    const options: OptionType[] =
      users
        ?.map((user: User) => ({ label: user.full_name, value: user._id }))
        .filter(({ label }) => !['Admin', 'Scheduler', 'Api'].includes(label)) ?? [];
    options.unshift({ label: 'Unassigned', value: null });
    return options;
  }, [users]);
};

export function Assignee() {
  const [assignee, setAssignee] = useState('');
  const options = useOptions();

  const handleSelect = (value: string) => {
    setAssignee(value);
  };

  const filterOptions = (input: string, option: any) => {
    if (!input || !option) {
      return true;
    }
    return String(option.children).toLowerCase().includes(input.toLowerCase());
  };

  return (
    <Form.Item label="Assignee" name="assignee">
      <Select
        value={assignee}
        onSelect={handleSelect}
        showSearch
        placeholder="Unassigned"
        optionFilterProp="children"
        filterOption={filterOptions}
      >
        {options.map((option) => (
          <Option key={option.value} value={option.value}>
            {option.label}
          </Option>
        ))}
      </Select>
    </Form.Item>
  );
}
