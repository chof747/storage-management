// hardwareItemConfig.ts
import { StorageElement } from '../../types/storageElements';
import { getItems, createItem, updateItem, deleteItem } from '../../api/storageElement';
import { FormField } from '../../components/common/ModelForm';
import { TableColumn } from '../../components/common/FilterableTable';
import { IconButton, Tooltip } from '@mui/material';
import { EntityConfig } from '../../components/common/ConfiguredEntityPage';
import { SettingsOutlined } from '@mui/icons-material';

export const formFields: FormField<Record<string, any>>[] = [
  { name: 'name', label: 'Name', required: true },
  { name: 'location', label: 'Location', required: true },
  { name: 'position', label: 'Position', required: true },
  { name: 'storage_type', label: 'Type of Storage', required: true },
  { name: 'description', label: 'Description', required: true },
];


export const tableColumns: TableColumn<StorageElement>[] = [
  { key: 'id', label: 'ID' },
  { key: 'name', label: 'Name', filterable: true },
  { key: 'location', label: 'Location', filterable: true },
  { key: 'position', label: 'Position' },
  { key: 'storage_type', label: 'Type', filterable: true },
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
  table: {
    columns: tableColumns,
    customActions: (item: StorageElement, refresh: () => void) => (
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
