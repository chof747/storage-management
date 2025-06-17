import MenuItem from "./menu/MenuItem";
import { List } from "@mui/material";
import BuildIcon from '@mui/icons-material/Build';
import { Inventory, Home } from "@mui/icons-material";
import LabelPrinting from '@mui/icons-material/LocalPrintshopTwoTone';
import CategoryIcon from '@mui/icons-material/Category';
import { openLabelPrintDialog } from "../../features/labelprint/useLabelPrintDialog";
import MenuActionItem from "./menu/MenuActionItem";

export const MenuDrawer = () => {

  return (
    <List>
      <MenuItem path="/" text="Home" Icon={Home} />
      <MenuItem path="/hardware" text="Hardware" Icon={BuildIcon} />
      <MenuItem path="/storage" text="Storage" Icon={Inventory} />
      <MenuItem path="/storage_type" text="Storage Types" Icon={CategoryIcon} />
      <MenuActionItem text="Print Labels ..." Icon={LabelPrinting} onClick={openLabelPrintDialog} />
    </List>
  );
};

export default MenuDrawer;