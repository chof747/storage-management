import { ListItemIcon, ListItemText, ListItemButton } from "@mui/material";
import { Link } from 'react-router-dom';

import { OverridableComponent } from '@mui/material/OverridableComponent';
import { SvgIconTypeMap } from '@mui/material/SvgIcon';

type IconComponent = OverridableComponent<SvgIconTypeMap<unknown, "svg">>;

export const MenuItem = ({ path, text, Icon }: {
  path: string,
  text: string,
  Icon: IconComponent
}) => {
  return (
    <ListItemButton component={Link} to={path}>
      <ListItemIcon>
        <Icon />
      </ListItemIcon>
      <ListItemText primary={text} />
    </ListItemButton>
  );
};

export default MenuItem;