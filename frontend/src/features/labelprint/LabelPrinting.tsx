import { useCallback, useEffect, useState } from "react";
import LabelPrintDialog from "../../components/dialogs/LabelPrintDialog";
import { printLabels } from "../../api/printLabels";
import { setLabelPrintTrigger } from "./useLabelPrintDialog";

const LabelPrintFeature: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [defaultStrategy, setDefaultStrategy] = useState('');

  const openDialog = useCallback((defaultStrategy?: string) => {
    if (defaultStrategy)
      setDefaultStrategy(defaultStrategy);
    setOpen(true);
  }, []);

  useEffect(() => {
    setLabelPrintTrigger(openDialog);
  }, [openDialog]);


  const handleClose = () => {
    setOpen(false);
  };

  const handlePrint = async (request: any) => {
    try {
      const pdfBlob = await printLabels(request);
      const pdfUrl = URL.createObjectURL(pdfBlob);
      window.open(pdfUrl, "_blank");
      handleClose();
    } catch (error) {
      console.error("Failed to generate PDF:", error);
      alert("Failed to generate PDF. Please try again.");
    }
  };

  return (
    <LabelPrintDialog
      open={open}
      onClose={handleClose}
      onSubmit={handlePrint}
      defaultStrategy={defaultStrategy}
    />
  );
};

export default LabelPrintFeature;
