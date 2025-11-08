import React, { useMemo, useState, useImperativeHandle, forwardRef, useEffect } from 'react';
import {
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  TableContainer,
  Paper,
  IconButton,
  TablePagination,
  Checkbox,
} from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon } from '@mui/icons-material';
import ConfirmDialog from './ConfirmDialog';
import FilterPanel from './FilterPanel'
import InlineCellEdit from "./InlineCellEdit";
import { ResultPage, QueryFilter } from '../../types/page';

/*
function getNestedValue(obj: any, path: string): any {
  return path.split('.').reduce((acc, part) => acc?.[part], obj);
}
*/

function getNestedValue<T, R = unknown>(obj: T, path: string): R | undefined {
  return path.split('.').reduce<unknown>((acc, part) => {
    if (typeof acc === 'object' && acc !== null && part in acc) {
      return (acc as Record<string, unknown>)[part];
    }
    return undefined;
  }, obj) as R | undefined;
}

export type TableColumn<T> = {
  key: keyof T;
  label: string;
  filterable?: boolean;
  filterKey?: string;
  editable?: boolean;
  render?: (value: T[keyof T], row: T) => React.ReactNode;
  onEditCommit?: (row: T, newValue: unknown) => Promise<void>;
};

type EditingState<T> = {
  rowId: string | number;
  colKey: keyof T;
  value: unknown;
  committing?: boolean;
} | null;

export type FilterableTableHandle<T> = {
  getSelectedItems: () => T[];
  refresh: () => void;
};

type FilterableTableProps<T> = {
  columns: TableColumn<T>[];
  fetchItems: (offset: number, limit: number, filters: QueryFilter[]) => Promise<ResultPage<T>>;
  onEdit?: (item: T) => void;
  onDelete?: (item: T) => void;
  getRowId: (item: T) => string | number;
  customActions?: (item: T, refresh: () => void) => React.ReactNode;
  selectableRows?: boolean;
  onSelectionChange?: (selectedItems: T[]) => void;
};

const FilterableTable = forwardRef(FilterableTableInner) as <T>(
  props: FilterableTableProps<T> & { ref?: React.Ref<FilterableTableHandle<T>> }
) => ReturnType<typeof FilterableTableInner>;

function FilterableTableInner<T>({
  columns,
  fetchItems,
  onEdit,
  onDelete,
  getRowId,
  customActions,
  selectableRows = false,
  onSelectionChange,
}: FilterableTableProps<T>, ref: React.Ref<FilterableTableHandle<T>>) {
  const initialFilterState = [] as QueryFilter[];

  const [items, setItems] = useState<T[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0); // zero-based
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [filters, setFilters] = useState(initialFilterState);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<T | null>(null);
  const [selectedIds, setSelectedIds] = useState<Set<string | number>>(new Set());
  const [editing, setEditing] = useState<EditingState<T>>(null);

  const filterConfig = columns
    .filter((col) => col.filterable)
    .map((col) => ({
      key: col.key as string,
      label: col.label,
    }));


  const allSelected = items.length > 0 && items.every((item) => selectedIds.has(getRowId(item)));

  const loadItems = async () => {
    const data = await fetchItems(page * rowsPerPage, rowsPerPage, filters);
    setItems(data.items);
    setTotal(data.total);
  };

  useEffect(() => {
    loadItems();
  }, [page, rowsPerPage, filters]);


  useImperativeHandle(ref, () => ({
    getSelectedItems: () => items.filter((item: T) => selectedIds.has(getRowId(item))),
    async refresh() {
      await loadItems();
    }
  }));

  const startEdit = (row: T, col: TableColumn<T>) => {
    if (!col.editable) return;
    const rowId = getRowId(row);
    setEditing({
      rowId,
      colKey: col.key,
      value: (row[col.key] ?? '') as unknown
    });
  };

  const commitEdit = async (row: T, col: TableColumn<T>, newValue: unknown) => {
    if (!col.onEditCommit) {
      setEditing(null);
      return;
    }
    const rowId = getRowId(row);
    setEditing((prev) => prev ? { ...prev, committing: true } : prev);

    try {
      await col.onEditCommit(row, newValue);
      await loadItems();
      setEditing(null);
    } catch (e) {
      setEditing((prev) => prev ? { ...prev, committing: false } : prev);
      // You might want to show a toast/snackbar here
      console.error('Edit commit failed:', e);
    }
  };

  const cancelEdit = () => setEditing(null);

  const updateFilter = (filters: QueryFilter[]) => {
    setFilters(filters);
  };

  const updateSelection = (updatedIds: Set<string | number>) => {
    setSelectedIds(updatedIds);
    if (onSelectionChange) {
      const selectedItems = items.filter((item) => updatedIds.has(getRowId(item)));
      onSelectionChange(selectedItems);
    }
  };

  const toggleSelectAll = () => {
    const updated = allSelected ? new Set<string | number>() : new Set(items.map(getRowId));
    updateSelection(updated);
  };

  const toggleSelectRow = (id: string | number) => {
    const updated = new Set(selectedIds);
    if (updated.has(id)) {
      updated.delete(id);
    } else {
      updated.add(id);
    }
    updateSelection(updated);
  };

  const openDeleteDialog = (item: T) => {
    setItemToDelete(item);
    setConfirmOpen(true);
  };

  const handleConfirmDelete = () => {
    if (itemToDelete && onDelete) {
      onDelete(itemToDelete);
    }
    setConfirmOpen(false);
    setItemToDelete(null);
  };

  const handleCancelDelete = () => {
    setConfirmOpen(false);
    setItemToDelete(null);
  };

  const generateSelectingCell = (id: string | number) => {
    if (selectableRows) {
      return (
        <TableCell padding="checkbox">
          <Checkbox
            checked={selectedIds.has(id)}
            onChange={() => toggleSelectRow(id)}
          />
        </TableCell>
      )
    } else {
      return null;
    }
  }

  const generateCell = (row: T, col: TableColumn<T>) => {
    const cellValue = row[col.key];
    if (!col.editable) {
      return (
        <TableCell key={col.key as string} sx={{ py: 0.5 }}>
          {col.render ? col.render(cellValue, row) : String(cellValue ?? '')}
        </TableCell>
      );
    } else {
      return (
        <TableCell key={String(col.key)} sx={{ py: 0.5 }}>
          <InlineCellEdit
            value={cellValue}
            editable
            renderDisplay={(v) => (col.render ? col.render(v, row) : String(v ?? ""))}
            onCommit={async (newVal) => {
              await col.onEditCommit?.(row, newVal);
              await loadItems();
            }}
          />
        </TableCell>
      );
    }
  }

  return (
    <>
      <FilterPanel onChange={updateFilter} config={filterConfig} />

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              {selectableRows && (
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={allSelected}
                    onChange={toggleSelectAll}
                    indeterminate={!allSelected && selectedIds.size > 0}
                  />
                </TableCell>
              )}
              {columns.map((col) => (
                <TableCell key={col.key as string}>{col.label}</TableCell>
              ))}
              {(onEdit || onDelete || customActions) && <TableCell align="right">Actions</TableCell>}
            </TableRow>
          </TableHead>
          <TableBody>
            {items.map((item) => {
              const id = getRowId(item);
              return (
                <TableRow key={id} hover selected={selectedIds.has(id)}>

                  {generateSelectingCell(id)}

                  {columns.map((col) => generateCell(item, col))}

                  {(onEdit || onDelete || customActions) && (
                    <TableCell align="right" sx={{ py: 0.5 }}>
                      {onEdit && (
                        <IconButton color="primary" onClick={() => onEdit(item)}>
                          <EditIcon />
                        </IconButton>
                      )}
                      {onDelete && (
                        <IconButton color="error" onClick={() => openDeleteDialog(item)}>
                          <DeleteIcon />
                        </IconButton>
                      )}
                      {customActions && customActions(item, () => setFilters({ ...filters }))}
                    </TableCell>
                  )}
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>

      <TablePagination
        component="div"
        count={total}
        page={page}
        onPageChange={(e, newPage) => setPage(newPage)}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={(e) => {
          setRowsPerPage(parseInt(e.target.value, 10));
          setPage(0);
        }}
      />

      <ConfirmDialog
        open={confirmOpen}
        title="Confirm Deletion"
        message="Are you sure you want to delete this item?"
        onConfirm={handleConfirmDelete}
        onCancel={handleCancelDelete}
        confirmText="Delete"
        cancelText="Cancel"
      />
    </>
  );
}

export default FilterableTable;
