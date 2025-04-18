import React, { useMemo, useState } from 'react';
import {
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  TableContainer,
  Paper,
  IconButton,
  Box,
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

type FilterableTableProps<T> = {
  data: T[];
  columns: TableColumn<T>[];
  onEdit?: (item: T) => void;
  onDelete?: (item: T) => void;
  getRowId: (item: T) => string | number;
  customActions?: (item: T, refresh: () => void) => React.ReactNode;
};

function FilterableTable<T>({
  data,
  columns,
  onEdit,
  onDelete,
  getRowId,
  customActions,
}: FilterableTableProps<T>) {
  const initialFilterState = columns.reduce((acc, col) => {
    if (col.filterable) acc[col.key as string] = '';
    return acc;
  }, {} as Record<string, string>);

  const [filters, setFilters] = useState(initialFilterState);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<T | null>(null);

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
        const column = columns.find(col => col.key === key);
        const fieldKey = column?.filterKey || key;
        const fieldValue = getNestedValue(item, fieldKey);
        return String(fieldValue ?? '').toLowerCase().includes(value.toLowerCase());
      })
    );
  }, [data, filters, columns]);

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

  return (
    <>
      <FilterPanel filters={filters} onChange={updateFilter} config={filterConfig} />

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              {columns.map((col) => (
                <TableCell key={col.key as string}>{col.label}</TableCell>
              ))}
              {(onEdit || onDelete) && <TableCell align="right">Actions</TableCell>}
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredData.map((item) => (
              <TableRow key={getRowId(item)}>
                {columns.map((col) => {
                  const value = item[col.key];
                  return (
                    <TableCell key={col.key as string}>
                      {col.render
                        ? col.render(item[col.key], item)
                        : String(item[col.key] ?? '')
                      }
                    </TableCell>
                  );
                })}
                {(onEdit || onDelete || customActions) && (
                  <TableCell align="right">
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
            ))}
          </TableBody>
        </Table>
      </TableContainer>

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
