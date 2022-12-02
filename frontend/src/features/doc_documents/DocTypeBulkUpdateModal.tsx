import { TypeFilterValue } from '@inovua/reactdatagrid-community/types';
import { TypeOnSelectionChangeArg } from '@inovua/reactdatagrid-community/types/TypeDataGridProps';
import { Button, Checkbox, Divider, Form, Modal, notification, Select } from 'antd';
import { useCallback, useEffect, useState } from 'react';
import { RemoteSelect } from '../../components';
import { DocumentTypes } from '../retrieved_documents/types';
import { useLazyGetAllDocIdsQuery } from '../sites/sitesApi';
import { useUpdateMultipleDocsMutation } from './docDocumentApi';
import { useFetchDocFamilyOptions } from './DocDocumentDocumentFamilyField';
import { useFetchPayerFamilyOptions } from '../payer-family/DocDocumentLocationForm';
import { useAppDispatch } from '../../app/store';

interface DocTypeBulkUpdateModalPropTypes {
  selection?: TypeOnSelectionChangeArg;
  filterValue: TypeFilterValue;
  siteId?: string;
  onBulkSubmit?: () => void;
}

export function DocTypeUpdateModal({
  selection,
  filterValue,
  onBulkSubmit,
  siteId,
}: DocTypeBulkUpdateModalPropTypes) {
  const [form] = Form.useForm();
  const [getAllDocIds] = useLazyGetAllDocIdsQuery();
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [open, setOpen] = useState(false);
  const [canOpen, setCanOpen] = useState(false);

  useEffect(() => {
    if (!selection) return;

    const selected = selection.selected;
    if (selected === true) {
      setCanOpen(true);
    } else if (typeof selected === 'object' && selected && Object.keys(selected).length > 0) {
      setCanOpen(true);
    } else {
      setCanOpen(false);
    }
  }, [selection]);

  const onOpen = useCallback(async () => {
    setOpen(true);
    form.resetFields();

    if (!selection) return;

    let ids: string[] = [];
    if (selection.selected === true) {
      ids = await getAllDocIds({ siteId, filterValue }).unwrap();
    }
    if (selection.selected && typeof selection.selected === 'object') {
      ids = Object.keys(selection.selected);
    }
    if (selection.unselected && typeof selection.unselected === 'object') {
      const unselected = selection.unselected;
      ids = ids.filter((id) => !unselected[id]);
    }
    setSelectedIds(ids);
  }, [setOpen, selection, form, getAllDocIds, setSelectedIds]);

  const [bulkUpdate, { isLoading }] = useUpdateMultipleDocsMutation();
  const dispatch = useAppDispatch();

  const handleSubmit = useCallback(async () => {
    const { document_type, document_family_id, payer_family_id, all_sites } =
      await form.validateFields();
    const ids = selectedIds;
    try {
      const update = {
        document_type,
        document_family_id,
      };
      const data = await bulkUpdate({
        ids,
        update,
        payer_family_id,
        site_id: siteId,
        all_sites,
      }).unwrap();
      notification.success({
        message: 'Documents Updated',
        description: `${data.count_success} Updates, ${data.count_error} Errors ${
          data.errors ? data.errors : ''
        }`,
      });
    } catch (err: any) {
      notification.error({
        message: 'Error Running Bulk Update',
        description: err.errors[0],
      });
    }
    onBulkSubmit?.();
    setOpen(false);
  }, [form, dispatch, siteId, selectedIds, bulkUpdate, notification, setOpen]);

  const onCancel = useCallback(async () => {
    setOpen(false);
  }, [setOpen]);

  const footer = (
    <div>
      <Button onClick={onCancel}>Cancel</Button>
      <Button type="primary" loading={isLoading} onClick={handleSubmit}>
        Submit
      </Button>
    </div>
  );

  const docType = Form.useWatch('document_type', form);
  const fetchDocFamilyOptions = useFetchDocFamilyOptions(form);
  const fetchPayerFamilyOptions = useFetchPayerFamilyOptions();

  const s = selectedIds.length > 1 ? 's' : '';
  return (
    <>
      <Button className="ml-auto" disabled={!canOpen} onClick={onOpen}>
        Bulk Update
      </Button>
      <Modal
        title={`${selectedIds.length} Document${s} Selected`}
        open={open}
        onCancel={onCancel}
        footer={footer}
      >
        <Form layout="vertical" requiredMark={false} form={form}>
          <Form.Item className="grow" name="document_type" label="Document Type">
            <Select options={DocumentTypes} showSearch />
          </Form.Item>
          <Form.Item className="grow" name="document_family_id" label="Document Family">
            <RemoteSelect
              allowClear
              disabled={!docType}
              className="w-full"
              fetchOptions={fetchDocFamilyOptions}
            />
          </Form.Item>
          <Divider />
          <Form.Item className="grow" name="payer_family_id" label="Payer Family">
            <RemoteSelect allowClear className="w-full" fetchOptions={fetchPayerFamilyOptions} />
          </Form.Item>
          {siteId ? (
            <div>
              <label className="mr-2">Apply to All Sites?</label>
              <Form.Item name="all_sites" valuePropName="checked" noStyle>
                <Checkbox />
              </Form.Item>
            </div>
          ) : null}
        </Form>
      </Modal>
    </>
  );
}
