export interface BaseDocument {
  _id: string;
}

export enum Status {
  Queued = 'QUEUED',
  Pending = 'PENDING',
  InProgress = 'IN_PROGRESS',
  Finished = 'FINISHED',
  Canceling = 'CANCELING',
  Canceled = 'CANCELED',
  Failed = 'FAILED',
}
