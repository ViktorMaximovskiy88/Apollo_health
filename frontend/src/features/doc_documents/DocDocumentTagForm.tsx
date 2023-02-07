import { useEffect, useState, useRef, useCallback } from 'react';
import { Radio, Checkbox, Input, Dropdown, Menu, Button } from 'antd';
import { debounce, orderBy } from 'lodash';
import { useVirtualizer } from '@tanstack/react-virtual';
import { DocumentTag, UITherapyTag } from './types';

import { EditTag, ReadTag } from './TagRow';
import { priorityOptions } from './useSiteDocDocumentColumns';
import { FilterTwoTone } from '@ant-design/icons';

function sortOrder(tags: any[], pageFilter: string) {
  if (pageFilter === 'page') {
    return orderBy(tags, ['page', '_normalized', '_type']);
  } else if (pageFilter === 'doc') {
    return orderBy(tags, ['_normalized', '_type', 'page']);
  } else {
    throw Error('what type though');
  }
}

function textFilter(tag: any, field: string, searchRegex: RegExp) {
  return tag[field] ? `${tag[field]}`.match(searchRegex) : false;
}

export function DocDocumentTagForm(props: {
  tags: Array<DocumentTag>;
  onDeleteTag: Function;
  onEditTag: Function;
  currentPage: number;
}) {
  const { tags, onEditTag, onDeleteTag, currentPage } = props;
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredList, setFilteredList] = useState(tags);
  const [tagTypeFilter, setTagTypeFilter] = useState<('focus' | 'indication' | 'therapy')[]>([
    'focus',
    'indication',
    'therapy',
  ]);
  const [priorityFilter, setPriorityFilter] = useState<
    ('Critical' | 'High' | 'Low' | 'No Priority')[]
  >(['Critical', 'High', 'Low']);
  const [editTags, setEditTags] = useState<{ [index: string]: DocumentTag }>({});
  const [pageFilter, setPageFilter] = useState('page');
  const [priorityDropdownOpen, setPriorityDropdownOpen] = useState(false);
  const [priorityFilterApplied, setPriorityFilterApplied] = useState(true);

  const tagFilterOptions = [
    { label: 'Focus', value: 'focus' },
    { label: 'Indication', value: 'indication' },
    { label: 'Therapy', value: 'therapy' },
  ];

  const handlePriorityFilterToggle = () => {
    if (!priorityFilterApplied) {
      setPriorityFilter(['Critical', 'High', 'Low']);
    }
    setPriorityFilterApplied(!priorityFilterApplied);
  };

  const priorityFilterOptions = (
    <Menu
      items={[
        {
          key: 'Filter',
          label: (
            <Button type="primary" onClick={handlePriorityFilterToggle}>
              {' '}
              {priorityFilterApplied ? 'Remove Filter' : 'Add Filter'}
            </Button>
          ),
        },
        ...priorityOptions.map((option: any) => {
          return {
            key: option.value,
            label: (
              <Checkbox
                indeterminate={!priorityFilterApplied}
                disabled={!priorityFilterApplied}
                value={option.label}
                checked={priorityFilterApplied && priorityFilter.includes(option.label)}
                onChange={(e) =>
                  setPriorityFilter((filter: any) => {
                    return e.target.checked
                      ? [...filter, e.target.value]
                      : filter.filter((x: any) => x !== e.target.value);
                  })
                }
              >
                {option.label}
              </Checkbox>
            ),
          };
        }),
      ]}
    />
  );

  const applyFilter = useCallback(
    (tag: DocumentTag) => {
      const validPage = pageFilter === 'doc' ? true : currentPage === tag.page;
      console.debug(currentPage === tag.page, 'currentPage', currentPage, 'tag.page', tag.page);
      let filter: boolean = tagTypeFilter.includes(tag._type) && validPage;
      if (tagTypeFilter.includes('focus')) {
        filter = filter && tag.focus ? tag.focus : false;
      }
      if (tag._type !== 'therapy' || !priorityFilterApplied) return filter;
      let priorFilter: boolean = false;
      for (const priority of priorityOptions) {
        if ((priorityFilter as any).includes(priority.label)) {
          priorFilter = tag.priority === priority.value;
          if (priorFilter) break;
        }
      }
      return filter && priorFilter;
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [pageFilter, currentPage, tagTypeFilter, priorityFilter]
  );

  const applyFilters = useCallback(() => {
    const regex = new RegExp(searchTerm, 'i');
    return tags.filter(
      (tag: any) =>
        (textFilter(tag, 'text', regex) ||
          textFilter(tag, 'code', regex) ||
          textFilter(tag, 'name', regex)) &&
        applyFilter(tag)
    );
  }, [searchTerm, tags, applyFilter]);

  useEffect(() => {
    const hasActiveFilters = pageFilter === 'page' || tagTypeFilter.length > 0 || searchTerm;
    let _tags = tags;

    if (hasActiveFilters) {
      _tags = applyFilters();
    }

    _tags = sortOrder(_tags, pageFilter);
    setFilteredList(_tags);
  }, [pageFilter, tagTypeFilter, searchTerm, applyFilters, tags, priorityFilterApplied]);

  const onSearch = (e: any) => {
    const search = e.target.value;
    setSearchTerm(search);
  };

  //  virtual list
  const parentRef = useRef() as React.MutableRefObject<HTMLDivElement>;
  const rowVirtualizer = useVirtualizer({
    count: filteredList.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 72,
    overscan: 10,
  });

  const handleToggleEdit = (
    tag: DocumentTag,
    editState: boolean,
    cancel: boolean = false,
    updateTags: boolean = false
  ) => {
    if (!editState && !cancel) {
      onEditTag(editTags[tag.id], updateTags);
    }
    setEditTags((prevState) => {
      const update = { ...prevState };
      if (editState === true) {
        update[tag.id] = { ...tag };
      } else {
        delete update[tag.id];
      }
      return update;
    });
  };

  const handleEditTag = (id: string, field: string, value: any) => {
    setEditTags((prevState) => {
      const update = { ...prevState };
      const target = update[id];
      if (field === 'name' || field === 'text' || field === 'update_status') {
        target[field] = value;
      } else if (field === 'page' && value != null) {
        target[field] = value - 1;
      } else if (field === 'focus') {
        (target as UITherapyTag)[field] = value;
      }
      return update;
    });
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex flex-col bg-white">
        <div className="flex flex-1 items-center">
          <Input.Search allowClear={true} placeholder="Search" onChange={debounce(onSearch, 250)} />
        </div>
        <div className="py-2 flex flex-1 space-x-2 items-center justify-between">
          <Radio.Group
            value={pageFilter}
            onChange={(e: any) => {
              setPageFilter(e.target.value);
            }}
            optionType="button"
            options={[
              { label: 'Page Tags', value: 'page' },
              { label: 'Doc Tags', value: 'doc' },
            ]}
          />
          <Checkbox.Group
            options={tagFilterOptions}
            value={tagTypeFilter}
            onChange={(values: any) => {
              setTagTypeFilter(values);
            }}
          />
          <div>
            {tagTypeFilter.includes('therapy') ? (
              <span>{priorityFilterApplied ? priorityFilter.length : 0} Filters Selected</span>
            ) : (
              <span>No Filter</span>
            )}
            <Dropdown.Button
              className="mr-4 h-full"
              type={priorityFilterApplied ? 'primary' : 'default'}
              disabled={!tagTypeFilter.includes('therapy')}
              open={priorityDropdownOpen}
              icon={
                <FilterTwoTone onClick={() => setPriorityDropdownOpen(!priorityDropdownOpen)} />
              }
              overlay={priorityFilterOptions}
            />
          </div>
        </div>
      </div>

      <div className="flex flex-col p-2 pr-4 overflow-auto bg-white flex-grow" ref={parentRef}>
        <div
          style={{
            height: `${rowVirtualizer.getTotalSize()}px`,
            position: 'relative',
          }}
        >
          {rowVirtualizer.getVirtualItems().map((virtualRow) => {
            const tag = filteredList[virtualRow.index];
            const readOnly = !editTags[tag.id];
            const existsCopy = tags.some((t) => t.name === tag.name && t.id !== tag.id);
            if (readOnly) {
              return (
                <ReadTag
                  key={tag.id}
                  onDeleteTag={onDeleteTag}
                  onToggleEdit={handleToggleEdit}
                  tag={tag}
                  virtualRow={virtualRow}
                  virtualizer={rowVirtualizer}
                />
              );
            } else {
              return (
                <EditTag
                  existsCopy={existsCopy}
                  key={tag.id}
                  onDeleteTag={onDeleteTag}
                  onEditTag={handleEditTag}
                  onToggleEdit={handleToggleEdit}
                  tag={tag}
                  virtualRow={virtualRow}
                  virtualizer={rowVirtualizer}
                />
              );
            }
          })}
        </div>
      </div>

      <div className="flex flex-col p-2 bg-white">
        <div className="flex flex-1 items-center justify-between">
          <div>
            Showing {filteredList.length} of {tags.length} Tags
          </div>
        </div>
      </div>
    </div>
  );
}
