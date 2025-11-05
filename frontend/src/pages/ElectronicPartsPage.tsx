import { getItems, togglePartforPrinting, resetCache, updatePartLabel } from "../api/electronicParts";
import FilterableTable, { TableColumn, FilterableTableHandle } from "../components/common/FilterableTable";
import { PartsBoxItem } from "../types/partsboxItems";
import { IconButton, Tooltip, Button } from '@mui/material';
import { PrintOutlined, PrintDisabled, Replay } from '@mui/icons-material';
import { useRef } from "react";


export default function ElectronicsPartsPage() {

  const obtainNewLabel = async (row: PartsBoxItem, current: string): string => {
    const newLabel = prompt("Enter new label", String(current));
    if (newLabel !== null) {
      row.label = newLabel;
    }
    else {
      row.label = '';
    }
    await updatePartLabel(row.id!, row.label);
    tableRef.current?.refresh();
    return row.label
  }

  const renderLabel = (value: string | number | boolean | undefined, row: PartsBoxItem): React.ReactNode => {
    return <>
      {
        <div onClick={() => {
          obtainNewLabel(row, value as string);
        }}> {value ? value : <i>(none)</i>}
        </div>
      }
    </>
  }

  const tableColumns: TableColumn<PartsBoxItem>[] = [
    { key: 'name', label: 'Name', filterable: true },
    { key: 'description', label: 'Description' },
    { key: 'label', label: 'Label', filterable: true, render: renderLabel },
    { key: 'storage_place', label: 'Place', filterable: true },
    { key: 'total_stock', label: 'Stock' },
  ];



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
      <div><Button
        startIcon={<Replay />}
        onClick={async () => {
          await resetCache();
          tableRef.current?.refresh();
        }
        }>Reload</Button></div>
    </>
  );
}