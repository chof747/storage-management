export interface HardwareItem {
  id?: number;
  hwtype: string;
  main_metric: string;
  secondary_metric?: string;
  length?: number;
  storage_element?: string;
  reorder?: boolean;
  reorder_link?: string;
}
