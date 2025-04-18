import FilterableTable, { TableColumn } from '../common/FilterableTable';
import { HardwareItem } from '../../types/hardwareItems';
import { ShoppingCart as ReorderIcon } from '@mui/icons-material';
import { IconButton, Tooltip } from '@mui/material';
import { PrintOutlined, PrintDisabled } from '@mui/icons-material';
import { toggleItemforPrinting } from '../../api/hardwareItem';

type Props = {
  items: HardwareItem[];
  onEdit: (item: HardwareItem) => void;
  onDelete: (id: number) => void;
  onRefresh: () => void;
};

const columns: TableColumn<HardwareItem>[] = [
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
    key: 'reorder', label: 'Reorder', filterable: true, render: (val, row) => {
      if (val) {
        return row.reorder_link
          ? <a href={row.reorder_link}><ReorderIcon color="warning" /></a>
          : <ReorderIcon />
      }
      else
        return null;
    }
  },
];


export default function HardwareItemTable({ items, onEdit, onDelete, onRefresh }: Props) {
  ;

  const handlePrintToggle = async (item: HardwareItem) => {
    await toggleItemforPrinting(item);
    onRefresh();
  }

  return (
    <FilterableTable
      data={items}
      columns={columns}
      onEdit={onEdit}
      onDelete={(item) => onDelete(item.id!)}
      customActions={(item) => (
        <Tooltip
          title={item.queued_for_printing ? "remove from queue" : "add to queue"}>

          <IconButton
            component="a"
            onClick={() => handlePrintToggle(item)}>
            {item.queued_for_printing
              ? <PrintDisabled />
              : <PrintOutlined color="secondary" />}
          </IconButton>
        </ Tooltip>
      )}
      getRowId={(item) => item.id!}
    />
  );
}
