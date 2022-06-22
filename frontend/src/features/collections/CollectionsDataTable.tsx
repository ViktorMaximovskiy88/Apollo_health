import ReactDataGrid from "@inovua/reactdatagrid-community";
import DateFilter from "@inovua/reactdatagrid-community/DateFilter";
import SelectFilter from "@inovua/reactdatagrid-community/SelectFilter";
import { Button, Spin } from "antd";
import { useCallback } from "react";
import { useDispatch, useSelector } from "react-redux";
import { collectionTableState, setCollectionTableFilter, setCollectionTableSort } from "../../app/uiSlice";
import { prettyDateDistance, prettyDateTimeFromISO } from "../../common";
import { ButtonLink } from "../../components/ButtonLink";
import { Status } from "../types";
import { useCancelSiteScrapeTaskMutation, useGetScrapeTasksForSiteQuery } from "./siteScrapeTasksApi";
import { SiteScrapeTask } from "./types";

const createColumns = (cancelScrape: any, isCanceling: boolean) => {
    return [
    {
      header: 'Start Time',
      name: 'queued_time',
      minWidth: 200,
      filterEditor: DateFilter,
      filterEditorProps: () => {
        return {
          dateFormat: 'YYYY-MM-DD',
          highlightWeekends: false,
          placeholder: 'Select Date'
        }
      },
      render: ({ value }: { value: string }) => {
        return prettyDateTimeFromISO(value);
      },
    },
    {
      header: 'Elapsed',
      minWidth: 300,
      defaultFlex: 1,
      render: ({ data: task }: { data: SiteScrapeTask }) => {
        return prettyDateDistance(task.queued_time, task.end_time);
      },
    },
    {
      header: 'Status',
      name: 'status',
      minWidth: 200,
      filterEditor: SelectFilter,
      filterEditorProps: { 
        placeholder: 'All',
        dataSource: [
          { id: Status.Queued, label: 'Queued' },
          { id: Status.InProgress, label: 'In Progress' },
          { id: Status.Finished, label: 'Finished' },
          { id: Status.Failed, label: 'Failed' },
          { id: Status.Canceling, label: 'Canceling' },
          { id: Status.Canceled, label: 'Canceled' },
        ]
      },
      render: ({ value: status }: { value: Status }) => {
        switch (status) {
          case Status.Failed:
            return <span className="text-red-500">Failed</span>;
          case Status.Canceled:
            return <span className="text-orange-500">Canceled</span>;
          case Status.Canceling:
            return (
              <>
                <span className="text-amber-500 mr-2">Canceling</span>
                <Spin size="small" />
              </>
            );
          case Status.InProgress:
            return <span className="text-blue-500">In Progress</span>;
          case Status.Queued:
            return <span className="text-yellow-500">Queued</span>;
          case Status.Finished:
            return <span className="text-green-500">Finished</span>;
          default:
            return null;
        }
      },
    },
    {
      header: 'Document Count',
      name: 'documents_found',
      defaultFlex: 1,
      minWidth: 300,
      render: ({ data: task }: { data: SiteScrapeTask }) => {
        const linksFound = `(${task.links_found} Links)`;
        const showLinksFounds =
          task.links_found > 0 && task.documents_found !== task.links_found;
        const docsCount = `${task.documents_found} Documents ${
          showLinksFounds ? linksFound : ''
        }`;

        return (
          <ButtonLink
            to={`/sites/${task.site_id}/documents?scrape_task_id=${task._id}`}
          >
            {docsCount}
          </ButtonLink>
        );
      },
    },
    {
      header: 'Actions',
      render: ({ data: task }: { data: SiteScrapeTask }) =>
        task.status === Status.InProgress || task.status === Status.Queued ? (
          <Button
            danger
            type="primary"
            disabled={isCanceling}
            onClick={() => cancelScrape(task._id)}
          >
            Cancel
          </Button>
        ) : null,
    },
  ];
}

export function CollectionsDataTable(props: { siteId: string }) {
  const siteId = props.siteId;
  const { data: scrapeTasks } = useGetScrapeTasksForSiteQuery(siteId, {
    pollingInterval: 3000,
    skip: !siteId,
  });
  const [cancelScrape, { isLoading: isCanceling }] =
    useCancelSiteScrapeTaskMutation();
    
  const columns = createColumns(cancelScrape, isCanceling);

  const tableState = useSelector(collectionTableState)
  const dispatch = useDispatch()
  const onFilterChange = useCallback((filter: any) => dispatch(setCollectionTableFilter(filter)), [dispatch]);
  const onSortChange = useCallback((sort: any) => dispatch(setCollectionTableSort(sort)), [dispatch]);

  return <>
    <ReactDataGrid
      dataSource={scrapeTasks || []}
      columns={columns}
      rowHeight={50}
      defaultFilterValue={tableState.filter}
      onFilterValueChange={onFilterChange}
      defaultSortInfo={tableState.sort}
      onSortInfoChange={onSortChange}
    />
  </>
}