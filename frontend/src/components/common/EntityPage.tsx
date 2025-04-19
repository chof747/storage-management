import { useEffect, useState } from 'react';
import {
  AppBar,
  Box,
  Button,
  Drawer,
  Toolbar,
  Typography,
} from '@mui/material';
import { ResultPage } from '../../types/page';

type EntityPageProps<T> = {
  title: string;
  fetchItems: (offset: number, limit: number) => Promise<ResultPage<T>>;
  createItem: (item: T) => Promise<T>;
  updateItem: (item: T) => Promise<T>;
  deleteItem: (id: number) => Promise<void>;
  FormComponent: React.ComponentType<{
    item: T | null;
    onSubmit: (item: T) => Promise<void>;
    onSuccess: () => void;
  }>;
  TableComponent: React.ComponentType<{
    items: T[];
    onEdit: (item: T) => void;
    onDelete: (id: number) => void;
    onRefresh: () => void;
    page: number;
    rowsPerPage: number;
    total: number;
    onPageChange: (page: number) => void;
    onRowsPerPageChange: (rowsPerPage: number) => void;
  }>;
  getItemId: (item: T) => number;
};

export default function EntityPage<T>({
  title,
  fetchItems,
  createItem,
  updateItem,
  deleteItem,
  FormComponent,
  TableComponent,
  getItemId,
}: EntityPageProps<T>) {
  const [items, setItems] = useState<T[]>([]);
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(0); // zero-based
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [selected, setSelected] = useState<T | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const loadItems = async () => {
    const data = await fetchItems(page * rowsPerPage, rowsPerPage);
    setItems(data.items);
    setTotal(data.total);
  };

  useEffect(() => {
    loadItems();
  }, [page, rowsPerPage]);

  const handleSubmit = async (item: T) => {
    if (selected) {
      await updateItem(item);
    } else {
      await createItem(item);
    }
  };

  const handleDelete = async (id: number) => {
    await deleteItem(id);
    loadItems();
  };

  const handleSuccess = () => {
    setDrawerOpen(false);
    setSelected(null);
    loadItems();
  };

  return (
    <>
      <AppBar position="static" sx={{ mb: 2 }}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            {title}
          </Typography>
          <Button color="inherit" onClick={() => {
            setSelected(null);
            setDrawerOpen(true);
          }}>
            Add Item
          </Button>
        </Toolbar>
      </AppBar>

      <Box>
        <TableComponent
          items={items}
          onEdit={(item) => {
            setSelected(item);
            setDrawerOpen(true);
          }}
          onDelete={(id) => handleDelete(id)}
          onRefresh={loadItems}
          page={page}
          rowsPerPage={rowsPerPage}
          total={total}
          onPageChange={setPage}
          onRowsPerPageChange={(val) => {
            setRowsPerPage(val);
            setPage(0);
          }}
        />

      </Box>

      <Drawer anchor="right" open={drawerOpen} onClose={() => setDrawerOpen(false)}>
        <Box width={400} p={2} pt={9}>
          <Typography variant="h6" gutterBottom>
            {selected ? 'Edit Item' : 'Add New Item'}
          </Typography>
          <FormComponent
            item={selected}
            onSubmit={handleSubmit}
            onSuccess={handleSuccess}
          />
        </Box>
      </Drawer>
    </>
  );
}
