import React, { useMemo, useState, useImperativeHandle, forwardRef } from 'react';
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
import FilterPanel from './FilterPanel';

function getNestedValue(obj: any, path: string): any {
  return path.split('.').reduce((acc, part) => acc?.[part], obj);
}

export type TableColumn<T> = {
  key: keyof T;
  label: string;
  filterable?: boolean;
  filterKey?: string;
  render?: (value: T[keyof T], row: T) => React.ReactNode;
};

export type FilterableTableHandle<T> = {
  getSelectedItems: () => T[];
};

type FilterableTableProps<T> = {
  data: T[];
  columns: TableColumn<T>[];
  onEdit?: (item: T) => void;
  onDelete?: (item: T) => void;
  getRowId: (item: T) => string | number;
  customActions?: (item: T, refresh: () => void) => React.ReactNode;
  page: number;
  rowsPerPage: number;
  total: number;
  onPageChange: (page: number) => void;
  onRowsPerPageChange: (rowsPerPage: number) => void;
  selectableRows?: boolean;
  onSelectionChange?: (selectedItems: T[]) => void;
};

function FilterableTableInner<T>({
  data,
  columns,
  onEdit,
  onDelete,
  getRowId,
  customActions,
  total,
  page,
  rowsPerPage,
  onPageChange,
  onRowsPerPageChange,
  selectableRows = false,
  onSelectionChange,
}: FilterableTableProps<T>, ref: React.Ref<FilterableTableHandle<T>>) {
  const initialFilterState = columns.reduce((acc, col) => {
    if (col.filterable) acc[col.key as string] = '';
    return acc;
  }, {} as Record<string, string>);

  const [filters, setFilters] = useState(initialFilterState);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<T | null>(null);
  const [selectedIds, setSelectedIds] = useState<Set<string | number>>(new Set());

  const filterConfig = columns
    .filter((col) => col.filterable)
    .map((col) => ({
      key: col.key as string,
      label: col.label,
    }));

  const updateFilter = (key: string, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const filteredData = useMemo(() => {
    if (!data?.length) return [];

    return data.filter((item) =>
      Object.entries(filters).every(([key, value]) => {
        const column = columns.find((col) => col.key === key);
        const fieldKey = column?.filterKey || key;
        const fieldValue = getNestedValue(item, fieldKey);
        return String(fieldValue ?? '').toLowerCase().includes(value.toLowerCase());
      })
    );
  }, [data, filters, columns]);

  const updateSelection = (updatedIds: Set<string | number>) => {
    setSelectedIds(updatedIds);
    if (onSelectionChange) {
      const selectedItems = filteredData.filter((item) => updatedIds.has(getRowId(item)));
      onSelectionChange(selectedItems);
    }
  };

  const allSelected = filteredData.length > 0 && filteredData.every((item) => selectedIds.has(getRowId(item)));

  const toggleSelectAll = () => {
    const updated = allSelected ? new Set<string | number>() : new Set(filteredData.map(getRowId));
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

  useImperativeHandle(ref, () => ({
    getSelectedItems: () => filteredData.filter((item) => selectedIds.has(getRowId(item))),
  }));

  return (
    <>
      <FilterPanel filters={filters} onChange={updateFilter} config={filterConfig} />

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
            {filteredData.map((item) => {
              const id = getRowId(item);
              return (
                <TableRow key={id} hover selected={selectedIds.has(id)}>
                  {selectableRows && (
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={selectedIds.has(id)}
                        onChange={() => toggleSelectRow(id)}
                      />
                    </TableCell>
                  )}
                  {columns.map((col) => (
                    <TableCell key={col.key as string} sx={{ py: 0.5 }}>
                      {col.render ? col.render(item[col.key], item) : String(item[col.key] ?? '')}
                    </TableCell>
                  ))}
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
        onPageChange={(e, newPage) => onPageChange(newPage)}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={(e) => onRowsPerPageChange(parseInt(e.target.value, 10))}
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

const FilterableTable = forwardRef(FilterableTableInner) as <T>(
  props: FilterableTableProps<T> & { ref?: React.Ref<FilterableTableHandle<T>> }
) => ReturnType<typeof FilterableTableInner>;

export default FilterableTable;
