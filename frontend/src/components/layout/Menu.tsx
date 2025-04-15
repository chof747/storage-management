import MenuItem from "./menu/MenuItem";
import { List } from "@mui/material";
import BuildIcon from '@mui/icons-material/Build';
import { Inventory } from "@mui/icons-material";
import { Home } from "@mui/icons-material";


export const MenuDrawer = () => {
  return (
    <List>
      <MenuItem path="/" text="Home" Icon={Home} />
      <MenuItem path="/hardware" text="Hardware" Icon={BuildIcon} />
      <MenuItem path="/storage" text="Storage" Icon={Inventory} />
    </List>
  );
};

export default MenuDrawer;