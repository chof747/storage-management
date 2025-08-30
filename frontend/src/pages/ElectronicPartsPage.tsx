import { getItems, togglePartforPrinting } from "../api/electronicParts";
import FilterableTable, { TableColumn, FilterableTableHandle } from "../components/common/FilterableTable";
import { PartsBoxItem } from "../types/partsboxItems";
import { IconButton, Tooltip } from '@mui/material';
import { PrintOutlined, PrintDisabled } from '@mui/icons-material';
import { useRef } from "react";

const tableColumns: TableColumn<PartsBoxItem>[] = [
  { key: 'name', label: 'Name', filterable: true },
  { key: 'description', label: 'Description' },
  { key: 'storage_place', label: 'Place', filterable: true },
  { key: 'total_stock', label: 'Stock' },
];


export default function ElectronicsPartsPage() {
  const tableRef = useRef<FilterableTableHandle<PartsBoxItem>>(null!) as React.RefObject<FilterableTableHandle<PartsBoxItem>>;

  return (
    <>
      <h2>Electronic Parts</h2>
      <FilterableTable<PartsBoxItem>
        ref={tableRef}
        fetchItems={getItems}
        columns={tableColumns}
        getRowId={(item) => item.id!}
        customActions={(item: PartsBoxItem) => (
          <Tooltip title={item.queued_for_printing ? "remove from queue" : "add to queue"}>
            <IconButton onClick={async () => {
              await togglePartforPrinting(item);
              tableRef.current?.refresh();
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