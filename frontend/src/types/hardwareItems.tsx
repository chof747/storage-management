import { StorageElement } from "./storageElements";

export interface HardwareItem {
  id?: number;
  hwtype: string;
  main_metric: string;
  secondary_metric?: string;
  length?: number;
  storage_element: StorageElement;
  reorder?: boolean;
  reorder_link?: string;
  queued_for_printing?: boolean;
}
