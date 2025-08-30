export interface ResultPage<T> {
  total: number,
  items: T[]
}

export type QueryFilter = {
  key: string;
  value: string;
};

