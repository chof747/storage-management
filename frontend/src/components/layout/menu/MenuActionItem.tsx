// src/components/layout/MenuActionItem.tsx
import { ListItemIcon, ListItemText, ListItemButton } from "@mui/material";
import { OverridableComponent } from '@mui/material/OverridableComponent';
import { SvgIconTypeMap } from '@mui/material/SvgIcon';

type IconComponent = OverridableComponent<SvgIconTypeMap<unknown, "svg">>;

interface Props {
  text: string;
  Icon: IconComponent;
  onClick: () => void;
}

const MenuActionItem = ({ text, Icon, onClick }: Props) => {
  return (
    <ListItemButton onClick={onClick}>
      <ListItemIcon>
        <Icon />
      </ListItemIcon>
      <ListItemText primary={text} />
    </ListItemButton>
  );
};

export default MenuActionItem;
