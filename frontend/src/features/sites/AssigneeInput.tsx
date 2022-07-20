import { Form, Input, AutoComplete } from 'antd';
import { FormInstance } from 'antd/lib/form/Form';
import { useState } from 'react';
import { useGetUsersQuery } from '../users/usersApi';

interface OptionType {
  label: string;
  value: string | null;
}

export function Assignee({ form }: { form: FormInstance }) {
  const { data } = useGetUsersQuery();
  const users: OptionType[] =
    data?.map((user) => ({ label: user.full_name, value: user._id })) ?? [];
  users.unshift({ label: 'Unassigned', value: null });
  const initialAssigneeId = form.getFieldValue('assignee');
  const [initialAssignee] = users.filter((user) => initialAssigneeId === user.value);
  const [value, setValue] = useState<string | null>(
    initialAssignee?.label === 'Unassigned' ? null : initialAssignee?.label ?? null
  );
  const [options, setOptions] = useState<OptionType[]>(users);

  const onSearch = (searchText: string) => {
    setOptions(
      searchText
        ? users.filter((user) => user.label.toLowerCase().includes(searchText.toLocaleLowerCase()))
        : users
    );
  };

  const onSelect = (assigneeId: string, option: OptionType) => {
    form.setFieldsValue({ assignee: assigneeId });
    const newAssigneeName = option.label === 'Unassigned' ? null : option.label;
    setValue(newAssigneeName);
  };

  const onChange = (data: any) => {
    setValue(data);
  };

  return (
    <>
      <Form.Item label="Assignee">
        <AutoComplete // element only displays fullname of selected assignee
          placeholder="Unassigned"
          value={value}
          options={options}
          onSelect={onSelect}
          onSearch={onSearch}
          onChange={onChange}
        />
      </Form.Item>
      <Form.Item // the element that actually saves the assignee user id
        hidden
        label="assignee id - should be hidden"
        name="assignee"
      >
        <Input />
      </Form.Item>
    </>
  );
}
