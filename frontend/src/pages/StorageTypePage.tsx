import { useRef } from "react";
import { FilterableTableHandle } from '../components/common/FilterableTable';
import { StorageType } from "../types/storageType";
import { StorageTypeConfig } from "./configurations/storagetype";
import ConfiguredEntityPage from "../components/common/ConfiguredEntityPage";


export default function StorageTypePage() {
  const storagetypeTableRef = useRef<FilterableTableHandle<StorageType>>(null) as React.RefObject<FilterableTableHandle<StorageType>>;
  return <ConfiguredEntityPage<StorageType> config={StorageTypeConfig} tableref={storagetypeTableRef} />;

}
