import React, { useEffect, useState } from "react";
import { HardwareItem } from "../../types/hardwareItems";
import { Box, Typography, TextField, Button, Dialog, DialogActions, DialogContent, DialogTitle } from "@mui/material";
import renderSelectWithCreate from "../../components/common/formitems/selectWithCreate";
import { FormField } from "../../components/common/ModelForm";
import { fetch_storage } from "../configurations/hardwareitem";

type MoveItemsDialogProps = {
  open: boolean;
  selectedItems: HardwareItem[];
  onClose: () => void;
  onSubmit: (targetStorageId: number, items: HardwareItem[]) => void;
};

const movetoField: FormField<Record<string, any>> = {
  name: 'moveto',
  label: 'Move to',
  type: 'select-create',
  required: true,
  loadOptions: fetch_storage
};

export default function MoveItemsDialog({
  selectedItems,
  onClose,
  onSubmit,
  open
}: MoveItemsDialogProps) {
  const [targetStorageId, setTargetStorageId] = React.useState<number | null>(null);
  const [options, setOptions] = useState<{ id: any; label: string }[]>([]);

  useEffect(() => {
    if (movetoField.loadOptions) {
      movetoField.loadOptions().then((opts) => {
        setOptions(opts);
      });
    }
  }, []);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setTargetStorageId(Number(e.target.value));
  };

  const handleSubmit = () => {
    if (targetStorageId !== null) {
      onSubmit(targetStorageId, selectedItems);
    }
  };


  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>Move Items</DialogTitle>
      <DialogContent>
        <Box display="flex" flexDirection="column" gap={2} mt={1}>
          <Typography>Move {selectedItems.length} item{selectedItems.length !== 1 && 's'} to:</Typography>
          {renderSelectWithCreate(
            movetoField,
            targetStorageId ?? "",
            undefined,
            handleChange,
            false,
            options,
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleSubmit}>Move</Button>
        <Button onClick={onClose}>Cancel</Button>
      </DialogActions>
    </Dialog >
  );

};