import { HardwareItem } from "../types/hardwareItems";

const API_BASE = "http://localhost:8000/api";

export const getItems = async (): Promise<HardwareItem[]> => {
  const res = await fetch(`${API_BASE}/items/`);
  return await res.json();
};

export const createItem = async (item: HardwareItem): Promise<HardwareItem> => {
  const res = await fetch(`${API_BASE}/items/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(item),
  });
  return await res.json();
};

export const updateItem = async (item: HardwareItem): Promise<HardwareItem> => {
  const res = await fetch(`${API_BASE}/items/${item.id}`, {
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
  await fetch(`${API_BASE}/items/${id}`, { method: "DELETE" });
};

export const toggleItemforPrinting = async (item: HardwareItem): Promise<void> => {
  const un = item.queued_for_printing ? "un" : ""
  const res = await fetch(`${API_BASE}/items/${un}queueforprinting/${item.id}`)
  if (!res.ok) {
    const error = new Error('Could not toggle printing state')
    throw error
  }
}