import { AutoComplete, Dropdown, Radio, Menu, Button, Input, Pagination } from 'antd';
import CodeMirror from '@uiw/react-codemirror';
import {
  CloseCircleOutlined,
  FileTextOutlined,
  InfoCircleOutlined,
  FileSearchOutlined,
  CodeOutlined,
} from '@ant-design/icons';
import { AppBreadcrumbs } from '../../app/AppLayout';
import { DevToolsLayout, ExtractedTextLoader, LinkDropDown } from '../../components';
import { useLazyGetDocumentsQuery, useLazySearchSitesQuery } from './devtoolsApi';
import { useDevToolsSlice } from './devtools-slice';
import { useTaskWorker } from '../tasks/taskSlice';
import { FileTypeViewer } from '../retrieved_documents/RetrievedDocumentViewer';
import { debounce } from 'lodash';
import { DevToolsDocRow } from './DevToolsDocRow';
import classNames from 'classnames';
import { DevToolsDoc } from './types';
import { useGetDocDocumentQuery } from '../doc_documents/docDocumentApi';
import { EditorView } from '@codemirror/view';
import { langs } from '@uiw/codemirror-extensions-langs';
import { prettyDateTimeFromISO } from '../../common';
import { PipelineStage } from '../../common/types';
import { CompareModal } from '../doc_documents/lineage/DocCompareToPrevious';
import { useEffect } from 'react';
import { useParams } from 'react-router-dom';

function DocActionMenu({ doc }: { doc: DevToolsDoc }) {
  const enqueueTask = useTaskWorker();
  return (
    <Menu
      onClick={(e: any) => {
        enqueueTask(e.key, { doc_doc_id: doc._id });
      }}
    >
      <Menu.Item key="ContentTask">Content Extraction</Menu.Item>
      <Menu.Item key="DateTask">Date Parsing</Menu.Item>
      <Menu.Item key="DocTypeTask">Doc Type Assignment</Menu.Item>
      <Menu.Item key="TagTask">Tag Classification</Menu.Item>
    </Menu>
  );
}

function ViewTypeSelect({ currentView, onChange }: { currentView: string; onChange: Function }) {
  return (
    <Radio.Group
      onChange={(e: any) => {
        onChange(e);
      }}
      defaultValue={currentView}
    >
      <Radio.Button value="info">
        <InfoCircleOutlined />
      </Radio.Button>
      <Radio.Button value="file">
        <FileSearchOutlined />
      </Radio.Button>
      <Radio.Button value="text">
        <FileTextOutlined />
      </Radio.Button>
      <Radio.Button value="json">
        <CodeOutlined />
      </Radio.Button>
    </Radio.Group>
  );
}

export function DevToolsPage({ showSiteFilter = false }: { showSiteFilter?: boolean }) {
  const { state, actions } = useDevToolsSlice();
  const { displayItems } = state;

  const params = useParams();
  const siteId = params.siteId ? params.siteId : state.selectedSite?._id;

  const [getDocuments] = useLazyGetDocumentsQuery();
  const [searchSites] = useLazySearchSitesQuery();

  useEffect(() => {
    getDocuments({
      site_id: siteId,
      search_query: state.docSearchQuery,
      page: state.pager.currentPage,
      limit: state.pager.perPage,
      sort: state.selectedSortBy.value,
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [siteId, state.docSearchQuery, state.pager, state.selectedSortBy]);

  useEffect(() => {
    actions.clearViewItem();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params]);

  const enqueueTask = useTaskWorker();
  const enqueueDiffTask = useTaskWorker((task: any) => {
    actions.setCompareResult(task.result);
    actions.toggleCompareModal(true);
  });

  return (
    <DevToolsLayout
      title={!showSiteFilter && <AppBreadcrumbs />}
      sectionToolbar={
        !showSiteFilter && (
          <>
            <Button
              disabled={state.viewItems.length !== 2}
              onClick={async () => {
                enqueueDiffTask('PDFDiffTask', {
                  previous_checksum: state.viewItems[0]?.item?.checksum,
                  current_checksum: state.viewItems[1]?.item?.checksum,
                });
              }}
              className="ml-auto"
            >
              Compare Docs
            </Button>
            <Button
              onClick={async () => {
                enqueueTask('SiteDocsPipelineTask', { site_id: siteId, reprocess: true });
              }}
              className="ml-auto"
            >
              Reprocess Site Docs
            </Button>
            <Button
              onClick={async () => {
                enqueueTask('LineageTask', { site_id: siteId, reprocess: true });
              }}
              className="ml-auto"
            >
              Reprocess Lineage
            </Button>
          </>
        )
      }
    >
      <div className="flex flex-row h-full">
        <div className="flex flex-col w-96 mr-2">
          {showSiteFilter && (
            <div className="bg-white h-8 mb-2 flex">
              <AutoComplete
                style={{ flex: '1' }}
                showSearch
                placeholder={'All Sites'}
                defaultActiveFirstOption={false}
                value={state.selectedSite?.name}
                showArrow={false}
                filterOption={false}
                notFoundContent={<div>No sites found</div>}
                fieldNames={{
                  label: 'name',
                  value: '_id',
                }}
                allowClear={true}
                options={state.siteOptions}
                dropdownMatchSelectWidth={false}
                onClear={() => {
                  actions.clearSiteSearch();
                  actions.selectSite();
                }}
                onSelect={(value: any, option: any) => {
                  actions.selectSite(option);
                }}
                onSearch={debounce((query) => {
                  if (query) {
                    searchSites(query);
                  } else {
                    actions.clearSiteSearch();
                  }
                }, 250)}
              >
                <Input />
              </AutoComplete>
            </div>
          )}
          <div className="bg-white h-8 mb-2">
            <Input.Search
              allowClear={true}
              placeholder="Search documents"
              onChange={debounce((e) => {
                actions.setDocSearchQuery(e.target.value);
              }, 250)}
            />
          </div>

          <div className="h-12 mb-2 flex justify-between">
            <div>
              <div className="text-xs">View as</div>
              <LinkDropDown
                width={'w-24'}
                selectedOption={state.selectedDefaultViewType}
                options={state.viewTypeOptions}
                onSelect={(option: any, index: number) => actions.selectDefaultViewType(option)}
              />
            </div>
            <div>
              <div className="text-xs">Sort by</div>
              <LinkDropDown
                width={'w-32'}
                selectedOption={state.selectedSortBy}
                options={state.sortByOptions}
                onSelect={(option: any, index: number) => actions.selectSortBy(option)}
              />
            </div>
            <div>
              <div className="text-xs">Group by</div>
              <LinkDropDown
                width={'w-24'}
                selectedOption={state.selectedGroupBy}
                options={state.groupByOptions}
                onSelect={(option: any, index: number) => actions.selectGroupBy(option)}
              />
            </div>
          </div>
          <div className="overflow-auto h-full bg-white border-slate-200 border-solid border">
            {displayItems.map((group) => (
              <div key={group.groupByKey} className="p-2 mb-1 border">
                {state.selectedGroupBy?.value && (
                  <div
                    className={classNames('text-slate-500 uppercase mb-1 cursor-pointer')}
                    onClick={() => {
                      actions.toggleCollapsed(group);
                    }}
                  >
                    {group.groupByKey} ({group.items.length})
                  </div>
                )}

                {!group.collapsed &&
                  group.items.map((item) => (
                    <DevToolsDocRow
                      key={item._id}
                      doc={item}
                      isSelected={false}
                      enableSplitView={!!state.viewItems.length}
                      setViewItem={actions.setViewItem}
                      setSplitItem={actions.setSplitItem}
                    />
                  ))}
              </div>
            ))}
          </div>

          <div className="h-8 p-2 flex justify-between">
            <Pagination
              total={state.pager.totalCount}
              current={state.pager.currentPage + 1}
              pageSize={state.pager.perPage}
              simple={true}
              onChange={(currentPage: number, perPage: number) =>
                actions.updatePager({ currentPage: currentPage - 1, perPage })
              }
            />
            <div>{state.pager.totalCount.toLocaleString()} total</div>
          </div>
        </div>

        <div className="flex flex-1 space-x-2">
          {state.viewItems.map(({ item, currentView }, i) => (
            <div
              key={`${item._id}-${i}`}
              className={classNames('h-full overflow-hidden flex-1 flex-col')}
            >
              <div className={classNames('h-8 m-1 flex justify-between items-center flex-nowrap')}>
                <div className="truncate">
                  <CloseCircleOutlined
                    onClick={() => {
                      actions.removeViewItemByIndex(i);
                    }}
                  />
                  &nbsp;
                  {item.name}
                </div>
              </div>
              <div className={classNames('m-2 flex justify-between')}>
                <div>
                  <ViewTypeSelect
                    currentView={state.selectedDefaultViewType.value}
                    onChange={(e: any) => {
                      actions.setViewItemDisplay({ index: i, viewKey: e.target.value });
                    }}
                  />
                </div>
                <div>
                  <Dropdown.Button
                    onClick={() => {
                      enqueueTask('DocPipelineTask', { doc_doc_id: item._id });
                    }}
                    overlay={<DocActionMenu doc={item} />}
                  >
                    Reprocess Doc
                  </Dropdown.Button>
                </div>
              </div>

              <DocDocumentViewer item={item} viewKey={currentView} />
            </div>
          ))}
        </div>
      </div>
      <CompareModal
        newFileKey={state.compareDocs.fileKeys[0]}
        prevFileKey={state.compareDocs.fileKeys[1]}
        modalOpen={state.compareDocs.showModal}
        handleCloseModal={() => actions.toggleCompareModal(false)}
      />
    </DevToolsLayout>
  );
}

export function DocDocumentViewer({ item, viewKey }: { item: DevToolsDoc; viewKey: string }) {
  return (
    <div className="h-full overflow-auto">
      {viewKey === 'json' && <DocumentJsonView docId={item._id} />}
      {viewKey === 'info' && <DocDocumentView docId={item._id} />}
      {viewKey === 'file' && <FileTypeViewer doc={item} docId={item.retrieved_document_id} />}
      {viewKey === 'text' && <ExtractedTextLoader docId={item.retrieved_document_id} />}
    </div>
  );
}

export function DocumentJsonView({ docId }: { docId: string }) {
  const { data } = useGetDocDocumentQuery(docId);
  // blacklist/nuke some _useless_ props
  const doc = { ...data, doc_vectors: ['redacted'] };
  return (
    <CodeMirror
      width="100%"
      height="calc(100vh - 150px)"
      readOnly={true}
      basicSetup={{
        bracketMatching: true,
        foldGutter: true,
        closeBrackets: true,
      }}
      extensions={[EditorView.lineWrapping, langs.json()]}
      value={JSON.stringify(doc, null, 2)}
    />
  );
}

function Field({ label, value }: { label: string; value: any }) {
  return (
    <div>
      <div className="font-semibold">{label}</div>
      <div className="mb-2">{value}</div>
    </div>
  );
}

function Section({ header, children }: { header: string; children: React.ReactNode }) {
  return (
    <>
      <h3 className="">{header}</h3>
      <div className="mb-6">{children}</div>
    </>
  );
}

function PipelineStageDisplay({ stage }: { stage: PipelineStage | undefined }) {
  return stage ? (
    <div>
      v{stage.version} at {prettyDateTimeFromISO(stage.version_at)}
    </div>
  ) : (
    <div>n/a</div>
  );
}

export function DocDocumentView({ docId }: { docId: string }) {
  const { data: doc } = useGetDocDocumentQuery(docId);
  return (
    <div>
      <Section header="Document Info">
        <Field label={'Name'} value={doc?.name} />
        <Field label={'Doc Type'} value={doc?.document_type} />
      </Section>
      <Section header="Pipeline Stages">
        <Field
          label={'Content'}
          value={<PipelineStageDisplay stage={doc?.pipeline_stages?.content} />}
        />
        <Field label={'Date'} value={<PipelineStageDisplay stage={doc?.pipeline_stages?.date} />} />
        <Field
          label={'Doc Type'}
          value={<PipelineStageDisplay stage={doc?.pipeline_stages?.doc_type} />}
        />
        <Field label={'Tag'} value={<PipelineStageDisplay stage={doc?.pipeline_stages?.tag} />} />
      </Section>
    </div>
  );
}
