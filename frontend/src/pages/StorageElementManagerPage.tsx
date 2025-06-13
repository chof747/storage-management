// StorageManagerPage.tsx
import { useLocation } from 'react-router-dom';
import { DriveFileMoveOutlined as MoveIcon } from '@mui/icons-material';
import LabelPrintingIcon from '@mui/icons-material/LocalPrintshopTwoTone';
import { getItems } from '../api/storageElement';
import { Box, Typography, IconButton, Table, TableRow, TableCell, TableBody, Divider } from '@mui/material';
import Layout from '../components/layout/Layout';
import { useEffect, useRef, useState } from 'react';
import { StorageElement } from '../types/storageElements';
import { ResultPage } from '../types/page';
import { HardwareItem } from '../types/hardwareItems';
import { getItemsByStorage, moveItemsBetweenStorages } from '../api/hardwareItem';
import { createHardwareItemConfig } from './configurations/hardwareitem';
import ConfiguredEntityPage, { EntityConfig } from '../components/common/ConfiguredEntityPage';
import { FilterableTableHandle } from '../components/common/FilterableTable';
import MoveItemsDialog from './dialogs/moveitems';
import { openLabelPrintDialog } from "../features/labelprint/useLabelPrintDialog";


export default function StorageElementManagerPage() {
  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const [element, setElement] = useState<StorageElement>();
  const [id] = useState<number>(Number(params.get('id')));
  const hwItemsTable = useRef<FilterableTableHandle<HardwareItem>>(null!) as React.RefObject<FilterableTableHandle<HardwareItem>>;
  const [openMoveDialog, setOpenMoveDialog] = useState(false);
  const [refreshToken, setRefreshToken] = useState(0);


  const loadElement = async (id: number) => {
    const elements: ResultPage<StorageElement> = await getItems(0, 1, id);
    if (1 == elements.total) {
      setElement(elements.items[0]);
    }
  };

  const boundGetItemsByStorage = (storageId: number) =>
    (offset: number, limit: number): Promise<ResultPage<HardwareItem>> =>
      getItemsByStorage(storageId, offset, limit);

  useEffect(() => {
    loadElement(id);
  }, [id]);

  const adaptedHWConfig = (): EntityConfig<HardwareItem> => {
    const config: EntityConfig<HardwareItem> = createHardwareItemConfig(
      refreshToken, setRefreshToken
    );
    config.fetchItems = boundGetItemsByStorage(id);
    config.title = `Items of ${element?.name}`;
    config.table.columns = config.table.columns.filter(col => col.key !== 'storage_element');
    config.toolbar = false;
    config.selectitems = true;

    return config;
  };

  const handleMoveClick = () => {
    setOpenMoveDialog(true);
  };

  const handleMoveSubmit = (targetStorageId: number, items: HardwareItem[]) => {
    setOpenMoveDialog(false);
    moveItemsBetweenStorages(items.map(item => item.id).filter((id): id is number => id !== undefined),
      targetStorageId).then(() => {
        hwItemsTable.current?.refresh();
      }
      ).catch((error) => {
        console.error("Error moving items:", error);
      }
      );
  };

  const rightPanel = (
    <>
      <Divider sx={{ height: 221, my: 1 }} />
      <Box>
        <Typography variant="subtitle1" gutterBottom>Actions</Typography>
        <IconButton onClick={handleMoveClick}
          component="label"><MoveIcon />
          <Typography variant="button">
            &nbsp;Move Items</Typography></IconButton><br />
        <IconButton
          component="label"
          onClick={() => openLabelPrintDialog(element?.storage_type?.printing_strategy)}>
          <LabelPrintingIcon />
          <Typography variant='button'>
            &nbsp;Print Labels</Typography></IconButton><br />

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
              <Typography variant="body1">{element?.storage_type?.name}</Typography>
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
        tableref={hwItemsTable}
      ></ConfiguredEntityPage>

      <MoveItemsDialog
        onSubmit={handleMoveSubmit}
        onClose={() => setOpenMoveDialog(false)}
        selectedItems={hwItemsTable.current?.getSelectedItems() ?? []}
        open={openMoveDialog}
      />
    </>
  );

  return (
    <Layout rightPanel={rightPanel}>
      {mainContent}
    </Layout>
  );
}
