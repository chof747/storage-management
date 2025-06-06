// hardwareItemConfig.ts
import { StorageElement } from '../../types/storageElements';
import { getItems, createItem, updateItem, deleteItem } from '../../api/storageElement';
import { getItems as getStorageTypeItems, createPlaceholder } from '../../api/storageType';
import { FormField } from '../../components/common/ModelForm';
import { TableColumn } from '../../components/common/FilterableTable';
import { IconButton, Tooltip } from '@mui/material';
import { EntityConfig } from '../../components/common/ConfiguredEntityPage';
import { SettingsOutlined } from '@mui/icons-material';
import { StorageType } from '../../types/storageType';

export const fetch_storage_types = async (): Promise<{ id: number; label: string }[]> => {
  const response = await getStorageTypeItems(0, 100);

  return response.items.filter((fi: StorageType) => (
    fi.id !== undefined
  )).map((se: StorageType) => ({
    id: se.id || 0,
    label: se.name
  }));
};


export const formFields: FormField<StorageElement>[] = [
  { name: 'name', label: 'Name', required: true },
  { name: 'location', label: 'Location', required: true },
  { name: 'position', label: 'Position', required: true },
  {
    name: 'storage_type_id',
    label: 'Type of Storage',
    type: 'select-create',
    required: true,
    loadOptions: fetch_storage_types,
    createNew: async () => {
      const name = prompt("New storage type name?");
      if (name !== null) {
        const newItem = await createPlaceholder(name);
        if (newItem.id !== undefined)
          return { id: newItem.id, label: newItem.name };
      }
      return { id: 0, label: '' };
    }
  },
  { name: 'description', label: 'Description', required: true },
];


export const tableColumns: TableColumn<StorageElement>[] = [
  { key: 'id', label: 'ID' },
  { key: 'name', label: 'Name', filterable: true },
  { key: 'location', label: 'Location', filterable: true },
  { key: 'position', label: 'Position' },
  {
    key: 'storage_type',
    label: 'Type',
    filterable: true,
    filterKey: 'storage_type.name',
    render: (val, item: StorageElement) => item?.storage_type?.name ?? '–',
  },
  //  { key: 'description', label: 'Description' },
];

export const storageElementConfig: EntityConfig<StorageElement> = {
  title: 'Storage Elements',
  fetchItems: getItems,
  createItem,
  updateItem,
  deleteItem,
  getItemId: (item: StorageElement) => item.id!,
  form: {
    fields: formFields,
  },
  toolbar: true,
  table: {
    columns: tableColumns,
    customActions: (item: StorageElement) => (
      <Tooltip title="manage storage">
        <IconButton
          component="a"
          href={`/storage/manage?id=${item.id}`}
          rel="noopener noreferrer">
          <SettingsOutlined />
        </IconButton>
      </Tooltip>
    ),
  }
};
