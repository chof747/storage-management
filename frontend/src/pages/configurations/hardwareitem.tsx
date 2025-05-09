// hardwareItemConfig.ts
import { HardwareItem } from '../../types/hardwareItems';
import { getItems, createItem, updateItem, deleteItem, toggleItemforPrinting } from '../../api/hardwareItem';
import { createPlaceholder } from '../../api/storageElement';
import { FormField } from '../../components/common/ModelForm';
import { TableColumn } from '../../components/common/FilterableTable';
import { ShoppingCart as ReorderIcon, PrintOutlined, PrintDisabled } from '@mui/icons-material';
import { IconButton, Tooltip } from '@mui/material';
import { EntityConfig } from '../../components/common/ConfiguredEntityPage';

const fetch_storage = async (): Promise<{ id: any; label: string }[]> => {
  const response = await fetch('http://localhost:8000/api/storage');
  const data = await response.json();
  return data.items.map((se: any) => ({
    id: se.id,
    label: se.name
  }));
};

export const formFields: FormField<Record<string, any>>[] = [
  { name: 'hwtype', label: 'Type', required: true },
  { name: 'main_metric', label: 'Main Metric', required: true },
  { name: 'secondary_metric', label: 'Secondary Metric' },
  { name: 'length', label: 'Length', type: 'number' },
  {
    name: 'storage_element_id',
    label: 'Stored in',
    type: 'select-create',
    loadOptions: fetch_storage,
    createNew: async () => {
      const name = prompt("New storage name?");
      if (name !== null) {
        const newItem = await createPlaceholder(name);
        return { id: newItem.id, label: newItem.name };
      }
      return { id: 0, label: '' };
    }
  },
  {
    name: 'reorder',
    label: 'Mark for Reordering',
    type: 'boolean',
  },
  {
    name: 'reorder_link',
    label: 'Reorder Link',
    type: 'text',
  },
];

export const tableColumns: TableColumn<HardwareItem>[] = [
  { key: 'id', label: 'ID' },
  { key: 'hwtype', label: 'Type', filterable: true },
  { key: 'main_metric', label: 'Main Metric', filterable: true },
  { key: 'secondary_metric', label: 'Secondary' },
  { key: 'length', label: 'Length' },
  {
    key: 'storage_element',
    label: 'Stored in',
    filterable: true,
    filterKey: 'storage_element.name',
    render: (val: any, item: HardwareItem) => item?.storage_element.name ?? '–',
  },
  {
    key: 'reorder',
    label: 'Reorder',
    filterable: true,
    render: (val, row) => row.reorder
      ? row.reorder_link
        ? <a href={row.reorder_link}><ReorderIcon color="warning" /></a>
        : <ReorderIcon />
      : ""
  },
];

export const createHardwareItemConfig = (): EntityConfig<HardwareItem> => ({
  title: 'Hardware Inventory',
  toolbar: true,
  fetchItems: getItems,
  createItem,
  updateItem,
  deleteItem,
  getItemId: (item: HardwareItem) => item.id!,
  form: {
    fields: formFields,
  },
  selectitems: false,
  table: {
    columns: tableColumns,
    customActions: (item: HardwareItem, refresh: () => void) => (
      <Tooltip title={item.queued_for_printing ? "remove from queue" : "add to queue"}>
        <IconButton onClick={async () => { await toggleItemforPrinting(item); refresh(); }}>
          {item.queued_for_printing
            ? <PrintDisabled />
            : <PrintOutlined color="secondary" />}
        </IconButton>
      </Tooltip>
    )
  }
});
