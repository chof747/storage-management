import { StorageType } from "./storageType";

export interface StorageElement {
  id?: number;
  name: string;
  location: string;
  position: string;
  storage_type?: StorageType;
  storage_type_id: number;
  description?: string;
}
