import { ResultPage, QueryFilter } from "../types/page";
import { getApiBase } from "./endpoint";
import { PartsBoxItem } from "../types/partsboxItems";

const PATH = "electronic-parts";

export const getItems = async (offset: number, limit: number, filters: QueryFilter[] = []): Promise<ResultPage<PartsBoxItem>> => {
  const API_BASE = await getApiBase();

  var filterParams = filters.map(f => `${encodeURIComponent(f.key)}:${encodeURIComponent(f.value)}`).join('&filter=');
  if (filterParams) {
    filterParams = '&filter=' + filterParams;
  }
  const res = await fetch(`${API_BASE}/${PATH}/?offset=${offset}&limit=${limit}${filterParams}`);
  return await res.json();
};

