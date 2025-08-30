import { getItems } from "../api/electronicParts";
import FilterableTable, { TableColumn } from "../components/common/FilterableTable";
import { PartsBoxItem } from "../types/partsboxItems";
import { IconButton, Tooltip } from '@mui/material';
import { PrintOutlined, PrintDisabled } from '@mui/icons-material';

const tableColumns: TableColumn<PartsBoxItem>[] = [
  { key: 'name', label: 'Name', filterable: true },
  { key: 'description', label: 'Description' },
  { key: 'storage_place', label: 'Place', filterable: true },
  { key: 'total_stock', label: 'Stock' },
];

export default function ElectronicsPartsPage() {
  return (
    <>
      <h2>Electronic Parts</h2>
      <FilterableTable<PartsBoxItem>
        fetchItems={getItems}
        columns={tableColumns}
        getRowId={(item) => item.id!}
        customActions={(item: PartsBoxItem) => (
          <Tooltip title={item.queued_for_printing ? "remove from queue" : "add to queue"}>
            <IconButton onClick={async () => {
              //await toggleItemforPrinting(item);
              //tableref.current?.refresh();
            }}>
              {item.queued_for_printing
                ? <PrintOutlined color="secondary" />
                : <PrintDisabled />}
            </IconButton>
          </Tooltip>
        )
        }
      />
    </>
  );
}