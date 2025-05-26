// hardwareItemConfig.ts
import { StorageType } from '../../types/storageType';
import { getItems, createItem, updateItem, deleteItem } from '../../api/storageType'
import { FormField } from '../../components/common/ModelForm';
import { TableColumn } from '../../components/common/FilterableTable';
import { EntityConfig } from '../../components/common/ConfiguredEntityPage';
import { getPrintStrategies } from '../../api/printStrategy';

export const fetch_print_strategies = async (): Promise<{ id: number; label: string }[]> => {
  const response = await getPrintStrategies();
  var i = 0;
  return response.map((ps: string) => ({
    id: i++,
    label: ps
  }));
};


export const formFields: FormField<StorageType>[] = [
  { name: 'name', label: 'Name', required: true },
  { name: 'printing_strategy', label: 'Printing Strategy', type: 'select', loadOptions: fetch_print_strategies, required: true },
  { name: 'description', label: 'Description', required: true },
];


export const tableColumns: TableColumn<StorageType>[] = [
  { key: 'id', label: 'ID' },
  { key: 'name', label: 'Name', filterable: true },
  { key: 'printing_strategy', label: 'Printing Strategy', filterable: true },
  { key: 'description', label: 'Description' },
];

export const StorageTypeConfig: EntityConfig<StorageType> = {
  title: 'Storage Types',
  fetchItems: getItems,
  createItem,
  updateItem,
  deleteItem,
  getItemId: (item: StorageType) => item.id!,
  form: {
    fields: formFields,
  },
  toolbar: true,
  table: {
    columns: tableColumns,
  }
};
