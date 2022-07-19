import { Button, Radio, Tag, Checkbox, Form, Select, Space, Switch, Input, DatePicker } from 'antd';
import { useForm } from 'antd/lib/form/Form';
import moment from 'moment';
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { prettyDate } from '../../common';
import { DocDocument } from './types';
import { BaseDocTag } from '../doc_documents/types';
import { useUpdateDocDocumentMutation } from './docDocumentApi';
import { FilterOutlined, DeleteOutlined } from '@ant-design/icons';
import debounce from 'lodash.debounce';
const { TextArea } = Input;

export function DocDocumentTagForm(props: { doc: DocDocument }) {
  const { doc } = props;

  const allTags: BaseDocTag[] = [...doc.therapy_tags, ...doc.indication_tags];

  const tags = [
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
    { text: 'Tag a', code: 'a', type: 'indication', page: 1 },
    { text: 'tag b', code: 'b', type: 'therapy', page: 2 },
    { text: 'tag c', code: 'c', type: 'therapy-group', page: 3 },
  ];

  const [searchTerm, setSearchTerm] = useState('');
  const [filteredList, setFilteredList] = useState(tags);
  const [tagTypeFilter, setTagTypeFilter] = useState(['indication', 'therapy', 'therapy-group']);
  const [pageFilter, setPageFilter] = useState('doc');

  const hasActiveFilters = () => {
    return pageFilter == 'page' || tagTypeFilter.length > 0 || searchTerm;
  };

  useEffect(() => {
    if (hasActiveFilters()) {
      applyFilters();
    } else {
      setFilteredList(tags);
    }
  }, [searchTerm, tagTypeFilter, pageFilter]);

  const applyFilter = (tag: any) => {
    const currentPage = 0;
    const validPage = pageFilter == 'doc' ? true : currentPage == tag.page;
    console.log(validPage, tagTypeFilter, tag.type);
    return tagTypeFilter.includes(tag.type) && validPage;
  };

  const applyFilters = () => {
    const regex = new RegExp(searchTerm, 'i');
    const filteredTags = tags.filter((tag: any) => {
      return (tag.text.match(regex) || tag.code.match(regex)) && applyFilter(tag);
    });
    setFilteredList(filteredTags);

    return;
  };

  const onSearch = (e: any) => {
    const search = e.target.value;
    setSearchTerm(searchTerm);
  };

  return (
    <>
      <div className="flex flex-col bg-white">
        <div className="flex flex-1 items-center">
          <Input.Search
            enterButton={<>Search</>}
            allowClear={true}
            placeholder="Search"
            onChange={debounce(onSearch, 250)}
          />
        </div>
        <div className="py-2 flex flex-1 space-x-2 items-center justify-between">
          <Radio.Group
            value={pageFilter}
            onChange={(e: any) => {
              console.log(e);
              setPageFilter(e.target.value);
            }}
            optionType="button"
            options={[
              { label: 'Doc Tags', value: 'doc' },
              { label: 'Page Tags', value: 'page' },
            ]}
          />
          <Checkbox.Group
            options={[
              { label: 'Indication', value: 'indication' },
              { label: 'Therapy', value: 'therapy' },
              { label: 'Therapy Group', value: 'therapy-group' },
            ]}
            value={tagTypeFilter}
            onChange={(e: any) => {
              setTagTypeFilter(e);
            }}
          />
          {/* 
          <Button>
            <FilterOutlined />
          </Button> */}
        </div>
      </div>

      <div className="flex flex-col p-2 h-full overflow-auto flex-1 h-[calc(100%_-_152px)]">
        {filteredList.map((tag) => (
          <div
            className="flex flex-row py-3"
            style={{ borderTop: '1px solid #ccc' }}
            key={tag.code}
          >
            <div className="flex flex-1">{tag.text}</div>
            <div className="">
              <Tag className="capitalize select-none cursor-default">{tag.type}</Tag>
            </div>
            <div className="flex">
              <DeleteOutlined
                className="cursor-pointer"
                onClick={(e) => {
                  console.log(e);
                }}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="flex flex-col bg-white">
        <div className="flex flex-1 pt-4 items-center justify-between">
          <div>
            Showing {filteredList.length} of {tags.length} Tags
          </div>
          <Button>Add Tag</Button>
        </div>
      </div>
    </>
  );
}
