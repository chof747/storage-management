// StorageManagerPage.tsx
import { useLocation } from 'react-router-dom';
import { DriveFileMoveOutlined as MoveIcon, DeleteOutlineOutlined as DeleteIcon } from '@mui/icons-material';
import { getItems } from '../api/storageElement';
import { Box, Typography, IconButton, Table, TableRow, TableCell, TableBody, Divider } from '@mui/material';
import Layout from '../components/layout/Layout';
import { useEffect, useState } from 'react';
import { StorageElement } from '../types/storageElements';
import { ResultPage } from '../types/page';
import { HardwareItem } from '../types/hardwareItems';
import { getItemsByStorage } from '../api/hardwareItem';
import { createHardwareItemConfig } from './configurations/hardwareitem';
import ConfiguredEntityPage, { EntityConfig } from '../components/common/ConfiguredEntityPage';

export default function StorageElementManagerPage() {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const [element, setElement] = useState<StorageElement>()
  const [id, setId] = useState<number>(Number(params.get('id')));

  const loadElement = async (id: number) => {
    const elements: ResultPage<StorageElement> = await getItems(0, 1, id)
    if (1 == elements.total) {
      setElement(elements.items[0])
    }
  }

  const boundGetItemsByStorage = (storageId: number) =>
    (offset: number, limit: number): Promise<ResultPage<HardwareItem>> =>
      getItemsByStorage(storageId, offset, limit);

  useEffect(() => {
    loadElement(id)
  }, [id])

  const adaptedHWConfig = (): EntityConfig<HardwareItem> => {
    const config: EntityConfig<HardwareItem> = createHardwareItemConfig()
    config.fetchItems = boundGetItemsByStorage(id);
    config.title = `Items of ${element?.name}`;
    config.table.columns = config.table.columns.filter(col => col.key !== 'storage_element');
    config.toolbar = false;
    config.selectitems = true;

    return config;
  };

  const rightPanel = (
    <>
      <Divider sx={{ height: 221, my: 1 }} />
      <Box>
        <Typography variant="subtitle1" gutterBottom>Actions</Typography>
        <IconButton
          component="label"><MoveIcon />
          <Typography variant="button">
            &nbsp;Move Items</Typography></IconButton><br />
        <IconButton><DeleteIcon /></IconButton>
        {/* Add more icons and labels as needed */}
      </Box>
    </>
  );


  const mainContent = (
    <>
      <h2>Manage {element?.name}</h2>
      <Table>
        <TableBody>
          <TableRow>
            <TableCell>
              <Typography variant="overline" >Location</Typography>
            </TableCell>
            <TableCell>
              <Typography variant="body1">{element?.location}</Typography>
            </TableCell>
            <TableCell>
              <Typography variant="overline" >Position</Typography>
            </TableCell>
            <TableCell>
              <Typography variant="body1">{element?.position}</Typography>
            </TableCell>
            <TableCell>
              <Typography variant="overline" >Type</Typography>
            </TableCell>
            <TableCell>
              <Typography variant="body1">{element?.storage_type}</Typography>
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell colSpan={6}>
              <Typography variant="overline">Description</Typography>
              <Typography variant="body1">{element?.description}</Typography>
            </TableCell>
          </TableRow>
        </TableBody>
      </Table>

      <Divider sx={{ backgroundColor: 'grey.400', height: 4, my: 1 }} />

      <ConfiguredEntityPage<HardwareItem>
        config={adaptedHWConfig()}
      ></ConfiguredEntityPage>
    </>
  )

  return (
    <Layout rightPanel={rightPanel}>
      {mainContent}
    </Layout>
  );
}
