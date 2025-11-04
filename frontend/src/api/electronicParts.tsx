import { ResultPage, QueryFilter } from "../types/page";
import { getApiBase } from "./endpoint";
import { PartsBoxItem } from "../types/partsboxItems";
import { buildFilterParams } from "./common";

const PATH = "electronic-parts";

export const getItems = async (offset: number, limit: number, filters: QueryFilter[] = []): Promise<ResultPage<PartsBoxItem>> => {
  const API_BASE = await getApiBase();

  const filterParams = buildFilterParams(filters);
  const res = await fetch(`${API_BASE}/${PATH}/?offset=${offset}&limit=${limit}${filterParams}`);
  return await res.json();
};

export const togglePartforPrinting = async (item: PartsBoxItem): Promise<void> => {
  const API_BASE = await getApiBase();
  const un = item.queued_for_printing ? "un" : "";
  const res = await fetch(`${API_BASE}/${PATH}/${un}queueforprinting/${item.id}`);
  if (!res.ok) {
    const error = new Error('Could not toggle printing state');
    throw error;
  }
};

export const resetCache = async (): Promise<void> => {
  const API_BASE = await getApiBase();
  const res = await fetch(`${API_BASE}/${PATH}/clear-cache/`);
  if (!res.ok) {
    const error = new Error('Could not reset cache');
    throw error;
  }
};