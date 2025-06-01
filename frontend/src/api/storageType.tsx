import { ResultPage } from "../types/page";
import { StorageType } from "../types/storageType";
import { getApiBase } from "./endpoint";

const PATH = "storagetype";
const API_BASE = await getApiBase()

export const getItems = async (offset: number, limit: number, id: number = 0): Promise<ResultPage<StorageType>> => {
  const res = await fetch(`${API_BASE}/${PATH}/${id > 0 ? id + "/" : ""}?offset=${offset}&limit=${limit}`);
  return await res.json();
};

export const createItem = async (item: StorageType): Promise<StorageType> => {
  const res = await fetch(`${API_BASE}/${PATH}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(item),
  });
  return await res.json();
};

export const createPlaceholder = async (name: string): Promise<StorageType> => {
  const item: StorageType = {
    id: 0,
    name: name,
  };
  return createItem(item);
};

export const updateItem = async (item: StorageType): Promise<StorageType> => {
  const res = await fetch(`${API_BASE}/${PATH}/${item.id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(item),
  });

  if (!res.ok) {
    const error = new Error('Update failed!') as Error & { response?: Response };
    error.response = res;
    throw error;
  }
  return await res.json();
};

export const deleteItem = async (id: number): Promise<void> => {
  await fetch(`${API_BASE}/${PATH}/${id}`, { method: "DELETE" });
};
