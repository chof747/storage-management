import MenuItem from "./menu/MenuItem";
import { List } from "@mui/material";
import BuildIcon from '@mui/icons-material/Build';
import { Home } from "@mui/icons-material";


export const MenuDrawer = () => {
  return (
    <List>
      <MenuItem path="/" text="Home" Icon={Home} />
      <MenuItem path="/hardware" text="Hardware" Icon={BuildIcon} />
    </List>
  );
};

export default MenuDrawer;