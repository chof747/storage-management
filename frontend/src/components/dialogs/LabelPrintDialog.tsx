import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Typography,
  IconButton,
  MenuItem
} from "@mui/material";
import { Delete } from "@mui/icons-material";
import { getPrintStrategies } from "../../api/printStrategy"; // Using the same API endpoint as in StorageTypePage
import { LabelPrintRequest, LabelSheet, StartPosition } from "../../types/labelPrintRequest";

interface LabelPrintDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (request: LabelPrintRequest) => void;
  defaultStrategy?: string;
}

const LabelPrintDialog: React.FC<LabelPrintDialogProps> = ({ open, onClose, onSubmit, defaultStrategy }) => {
  const [sheets, setSheets] = useState<LabelSheet[]>([]);
  const [strategy, setStrategy] = useState<string>("");
  const [strategies, setStrategies] = useState<string[]>([]);

  useEffect(() => {
    if (open) {
      setSheets([{ start_pos: { row: 1, col: 1 } }]);

      getPrintStrategies().then((data) => {
        setStrategies(data);
        if (data.length > 0 && !defaultStrategy) {
          setStrategy(data[0]);
        } else if (defaultStrategy) {
          //set default strategy only here as then the values are filled
          setStrategy(defaultStrategy)
        }
      });
    }
  }, [open]);

  const handleAddSheet = () => {
    setSheets([...sheets, { start_pos: { row: 1, col: 1 } }]);
  };

  const handleRemoveSheet = (index: number) => {
    const updatedSheets = [...sheets];
    updatedSheets.splice(index, 1);
    setSheets(updatedSheets);
  };

  const handleSheetChange = (index: number, field: keyof StartPosition, value: number) => {
    const updatedSheets = [...sheets];
    updatedSheets[index].start_pos[field] = value;
    setSheets(updatedSheets);
  };

  const handleSubmit = () => {
    onSubmit({ sheets, strategy });
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Label Printing</DialogTitle>
      <DialogContent>
        <Typography variant="subtitle1" gutterBottom>
          Define the sheets to print labels for:
        </Typography>
        {sheets.map((sheet, index) => (
          <Box key={index} display="flex" alignItems="center" gap={2} mb={1}>
            <Typography variant='subtitle2'>Sheet {index + 1}:</Typography>
            <TextField
              label="Row"
              type="number"
              value={sheet.start_pos.row}
              onChange={(e) => handleSheetChange(index, "row", parseInt(e.target.value))}
              size="small"
            />
            <TextField
              label="Col"
              type="number"
              value={sheet.start_pos.col}
              onChange={(e) => handleSheetChange(index, "col", parseInt(e.target.value))}
              size="small"
            />
            <IconButton onClick={() => handleRemoveSheet(index)} size="small" color="error">
              <Delete />
            </IconButton>
          </Box>
        ))}
        <Button variant="outlined" onClick={handleAddSheet}>
          Add Sheet
        </Button>

        <Box mt={2}>
          <TextField
            label="Strategy"
            select
            value={strategy}
            onChange={(e) => setStrategy(e.target.value)}
            fullWidth
            size="small"
          >
            {strategies.map((s) => (
              <MenuItem key={s} value={s}>
                {s}
              </MenuItem>
            ))}
          </TextField>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSubmit} variant="contained" color="primary" disabled={sheets.length === 0}>
          Print
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default LabelPrintDialog;
