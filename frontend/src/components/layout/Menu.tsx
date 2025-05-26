import MenuItem from "./menu/MenuItem";
import { List } from "@mui/material";
import BuildIcon from '@mui/icons-material/Build';
import { Inventory, Home, } from "@mui/icons-material";
import CategoryIcon from '@mui/icons-material/Category';

export const MenuDrawer = () => {
  return (
    <List>
      <MenuItem path="/" text="Home" Icon={Home} />
      <MenuItem path="/hardware" text="Hardware" Icon={BuildIcon} />
      <MenuItem path="/storage" text="Storage" Icon={Inventory} />
      <MenuItem path="/storage_type" text="Storage Types" Icon={CategoryIcon} />
    </List>
  );
};

export default MenuDrawer;