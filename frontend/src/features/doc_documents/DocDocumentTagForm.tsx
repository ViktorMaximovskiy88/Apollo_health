import { Button, Radio, Tag, Form, Select, Space, Switch, Input, DatePicker } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import moment from 'moment';
import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { prettyDate } from '../../common';
import { DocDocument } from './types';
import { useUpdateDocDocumentMutation } from './docDocumentApi';
import { FilterOutlined } from '@ant-design/icons';
const { TextArea } = Input;

export function DocDocumentTagForm(props: { doc: DocDocument }) {
  const tags = [
    { title: 'Tag 1', tagType: 'Indication' },
    { title: 'Tag 1', tagType: 'Indication' },
    { title: 'Tag 1', tagType: 'Indication' },
    { title: 'Tag 1', tagType: 'Indication' },
    { title: 'Tag 1', tagType: 'Indication' },
    { title: 'Tag 1', tagType: 'Indication' },
    { title: 'Tag 1', tagType: 'Indication' },
    { title: 'Tag 1', tagType: 'Indication' },
    { title: 'Tag 1', tagType: 'Indication' },
    { title: 'Tag 1', tagType: 'Indication' },
    { title: 'Tag 1', tagType: 'Indication' },
    { title: 'Tag 1', tagType: 'Indication' },
    { title: 'Tag 1', tagType: 'Indication' },
    { title: 'Tag 1', tagType: 'Indication' },
    { title: 'Tag 1', tagType: 'Indication' },
    { title: 'Tag 1', tagType: 'Indication' },
  ];

  return (
    <div>
      <div className="flex">
        <div className="flex flex-1 items-center">
          <Input placeholder="Search" />
        </div>
        <div className="flex flex-1 space-x-2 items-center justify-end">
          <Radio.Group
            optionType="button"
            options={[
              { label: 'Doc Tags', value: 'doc' },
              { label: 'Page Tags', value: 'page' },
            ]}
          />
          <Button>
            <FilterOutlined />
          </Button>
        </div>
      </div>

      <div className="flex flex-col p-2">
        {tags.map((tag) => (
          <div className="flex flex-row py-2">
            <div className="flex flex-1">{tag.title}</div>
            <div className="">
              <Tag>{tag.tagType}</Tag>
            </div>
            <div className="flex flex-1"></div>
          </div>
        ))}
      </div>
    </div>
  );
}
