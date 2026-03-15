export type QueueId = string;
export type QueueItemId = string;

export type QueueOperation = "create" | "update" | "delete";

export enum QueueStatus {
  OPEN = "OPEN",
  PAUSED = "PAUSED",
  DISPATCHING = "DISPATCHING",
  COMPLETED = "COMPLETED"
}

export interface QueueScheduling {
  day_key: string;
  start_time: string;
  end_time: string;
  interval: string;
}

export interface QueueItem {
  item_id: string;
  queue_id: string;
  operation: QueueOperation;
  scheduling: QueueScheduling;
  payload: Record<string, unknown>;
  metadata: Record<string, unknown>;
}

export interface Queue {
  id: string;
  status: QueueStatus;
  items: QueueItem[];
}

export interface BuildQueueItemInput {
  queue_id: QueueId;
  item_id: QueueItemId;
  block_id: string;
  operation: QueueOperation;
  day: string;
  start_time: string;
  end_time: string;
  interval?: string;
  payload?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

function newUuid(): string {
  if (typeof globalThis.crypto?.randomUUID === "function") {
    return globalThis.crypto.randomUUID();
  }

  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function createQueueId(): QueueId {
  return newUuid();
}

export function createQueueItemId(): QueueItemId {
  return newUuid();
}

export function buildQueueItem(input: BuildQueueItemInput): QueueItem {
  const interval = input.interval ?? `${input.start_time} - ${input.end_time}`;
  const metadata: Record<string, unknown> = {
    ...(input.metadata ?? {})
  };

  if (metadata.block_id === undefined) {
    metadata.block_id = input.block_id;
  }

  return {
    item_id: input.item_id,
    queue_id: input.queue_id,
    operation: input.operation,
    scheduling: {
      day_key: input.day,
      start_time: input.start_time,
      end_time: input.end_time,
      interval
    },
    payload: input.payload ?? {},
    metadata
  };
}

export const create_queue_id = createQueueId;
export const create_queue_item_id = createQueueItemId;
export const build_queue_item = buildQueueItem;
