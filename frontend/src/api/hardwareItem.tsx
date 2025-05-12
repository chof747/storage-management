import { HardwareItem } from "../types/hardwareItems";
import { ResultPage } from "../types/page";

const API_BASE = "http://localhost:8000/api";
const PATH = '/items';

export const getItems = async (offset: number, limit: number): Promise<ResultPage<HardwareItem>> => {
  const res = await fetch(`${API_BASE}${PATH}/?offset=${offset}&limit=${limit}`);
  return await res.json();
};

export const getItemsByStorage = async (storageId: number,
  offset: number, limit: number): Promise<ResultPage<HardwareItem>> => {
  const res = await fetch(`${API_BASE}${PATH}/bystorage/?storage=${storageId}&offset=${offset}&limit=${limit}`);
  return await res.json();
};

export const createItem = async (item: HardwareItem): Promise<HardwareItem> => {
  const res = await fetch(`${API_BASE}${PATH}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(item),
  });
  return await res.json();
};

export const updateItem = async (item: HardwareItem): Promise<HardwareItem> => {
  const res = await fetch(`${API_BASE}${PATH}/${item.id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(item),
  });

  if (!res.ok) {
    const error = new Error('Update failed!') as Error & { response?: Response }
    error.response = res;
    throw error;
  }
  return await res.json();
};

export const deleteItem = async (id: number): Promise<void> => {
  await fetch(`${API_BASE}${PATH}/${id}`, { method: "DELETE" });
};

export const toggleItemforPrinting = async (item: HardwareItem): Promise<void> => {
  const un = item.queued_for_printing ? "un" : ""
  const res = await fetch(`${API_BASE}${PATH}/${un}queueforprinting/${item.id}`)
  if (!res.ok) {
    const error = new Error('Could not toggle printing state')
    throw error
  }
}

export const moveItemsBetweenStorages = async (itemIds: number[], storageId: number): Promise<void> => {
  const res = await fetch(`${API_BASE}${PATH}/move`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      items: itemIds,
      storage_to: storageId
    })
  });

  if (!res.ok) {
    const error = new Error('Could not move items')
    throw error
  }
  return await res.json();
}