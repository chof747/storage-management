import { ResultPage } from "../types/page";
import { StorageElement } from "../types/storageElements";
import { getApiBase } from "./endpoint";

const PATH = "storage";

export const getItems = async (offset: number, limit: number, id: number = 0): Promise<ResultPage<StorageElement>> => {
  const API_BASE = await getApiBase()
  const res = await fetch(`${API_BASE}/${PATH}/${id > 0 ? id + "/" : ""}?offset=${offset}&limit=${limit}`);
  return await res.json();
};

export const createItem = async (item: StorageElement): Promise<StorageElement> => {
  const API_BASE = await getApiBase()
  const res = await fetch(`${API_BASE}/${PATH}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(item),
  });
  return await res.json();
};

export const createPlaceholder = async (name: string): Promise<StorageElement> => {
  const API_BASE = await getApiBase()
  const item: StorageElement = {
    name: name,
    location: '',
    position: '',
    storage_type_id: 1
  };
  return createItem(item);
};

export const updateItem = async (item: StorageElement): Promise<StorageElement> => {
  const API_BASE = await getApiBase()
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
  const API_BASE = await getApiBase()
  await fetch(`${API_BASE}/${PATH}/${id}`, { method: "DELETE" });

};

export const markAllForPrinting = async (id: number): Promise<void> => {
  const API_BASE = await getApiBase()
  await fetch(`${API_BASE}/${PATH}/markallforprinting/${id}`, { method: "POST" })
}
