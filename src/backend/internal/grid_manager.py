import io
import zipfile
import json
from bitarray import bitarray
from typing import cast
from src.backend.internal.grid_handler import GridHandler


class GridManager:
    """
    Manages all GridHandler Instances
    """

    def __init__(self):
        self.requires_sync = True
        self.all_grids = {}
        self.setup_grid_handlers()
        self.existing_names = {"DAY1": set(), "DAY2": set(), "DAY3": set()}
        self.all_hours = {
            "TOTAL": {
                "Name": "TOTAL",
                "Day 1": 0,
                "Day 2": 0,
                "Day 3": 0,
                "Total": 0,
            }
        }

    def setup_grid_handlers(self):
        """
        Set up required grid_handler class instances

        This method is called automatically upon class instantiation
        """
        all_locations = ["MCC", "HCC1", "HCC2"]
        for location in all_locations:
            for i in range(1, 4):
                if i == 3 and location != "MCC":
                    continue
                self.all_grids[f"DAY{i}:{location}"] = GridHandler(
                    location=location, day=i
                )

    def format_keys(
        self,
        reference_time_blocks: list[str],
        bit_mask_1: bitarray,
        bit_mask_2: bitarray = None,
        bit_mask_3: bitarray = None,
    ) -> list[str]:
        """
        Aligns timeblocks across 3 dataframes based on identical scheduling.

        This function reads up to 3 bitsets representing whether two 30 min time block pairs can be joined,
        and returns a list of formatted time keys and a corresponding list indicating
        whether consecutive blocks can be joined.


        Args:
            df1 (bitarray): The first bitarray
            df2 (bitarray): The second bitarray. Can be None.
            df3 (bitarray): The third bitarray. Can be None.


        Returns:
            list[str]: A list where:
                - each element is a time block that can be combined to a 1h block (e.g. "08:30", can be combined with "08:00")
                - the elements will always be the second half of the hour "xx:30"
        """
        blocks_to_remove = []
        result_mask = bit_mask_1.copy()
        if bit_mask_2 is not None:
            result_mask &= bit_mask_2
        if bit_mask_3 is not None:
            result_mask &= bit_mask_3

        for block, remove in zip(reference_time_blocks, result_mask):
            if remove:
                blocks_to_remove.append(block)

        return blocks_to_remove

    def update_existing_names(self, day: int):
        """
        update the self.existing name attribute for a specified day
        - used to track which names are already allocated for in a day
        - prevents allocating the same name to different grids on the same day

        Args:
            day (int): Which day to update
        """
        new_set = set()
        for key, grid_handler in self.all_grids.items():
            if f"DAY{day}" in key:
                new_set = new_set.union(grid_handler.get_names())
        self.existing_names[f"DAY{day}"] = new_set

    def name_exists(self, name, day: int) -> bool:
        """
        Checks if a name already exists in any DAY{x} grid
        Args:
            day (int)
        Returns:
            True if name exists else False
        """
        return name in self.existing_names[f"DAY{day}"]

    def get_all_hours(self) -> list[dict]:
        """
        Return data from all_hours attribute as rowData for aggrid
        """
        row_data = []
        pinned_row_data = []
        for data in self.all_hours.values():
            if data["Name"] == "TOTAL":
                pinned_row_data.append(data)
            else:
                row_data.append(data)

        return row_data, pinned_row_data

    def update_hours(self, name: str, target_grid: str):
        """
        Update hour data for a specified name and target_grid
        - This method is called when making changes to underlying grid handler for incremental update
        - The self.all_hours attribute is updated
        """

        def __update_day_hours(day: int, name: str, new_hours):
            key = f"Day {day}"
            name_hour_data = self.all_hours[name]
            total_hour_data = self.all_hours["TOTAL"]
            # update hours for that name and the overall total hours
            total_hour_data[key] -= name_hour_data[key]
            total_hour_data["Total"] -= name_hour_data[key]
            name_hour_data["Total"] -= name_hour_data[key]
            name_hour_data[key] = new_hours
            total_hour_data[key] += name_hour_data[key]
            total_hour_data["Total"] += name_hour_data[key]
            name_hour_data["Total"] += name_hour_data[key]

        handler = self.all_grids[target_grid]
        handler = cast(GridHandler, handler)
        name_exists = False
        #check if name exists
        for names in self.existing_names.values():
            if name in names:
                name_exists = True
                break
        #name no longer exists, remove all entry of this name
        if not name_exists:
            __update_day_hours(handler.day,name,0)
            self.all_hours.pop(name, None)
            return
        if not handler.name_exists(name):  # name has been removed
            __update_day_hours(handler.day, name, 0)
            return
        if name not in self.all_hours:  # name has just been added
            self.all_hours[name] = {
                "Name": name,
                "Day 1": 0,
                "Day 2": 0,
                "Day 3": 0,
                "Total": 0,
            }
            return

        hour_data = handler.get_hours()
        __update_day_hours(handler.day, name, hour_data[name])

    def serialise_to_zip(self):
        """
        Serialise GridManager and all GridHandler instances to zip

        Returns:
            bytes: zip file containing all serialised GridHandlers
        """
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            manager_info = {
                "all_hours": self.all_hours,
                "existing_names": {k: list(v) for k, v in self.existing_names.items()},
                "handler_keys": list(self.all_grids.keys()),
                "total_handlers": len(self.all_grids),
            }
            zip_file.writestr("manager_info.json", json.dumps(manager_info))
            for key, handler in self.all_grids.items():
                key = key.replace(":", "_")
                handler = cast(GridHandler, handler)
                metadata, df_bytes = handler.serialise_for_storage()

                handler_folder = f"handlers/{key}/"

                metadata_filename = f"{handler_folder}metadata.json"
                zip_file.writestr(metadata_filename, json.dumps(metadata))

                dataframe_filename = f"{handler_folder}dataframe.parquet"
                zip_file.writestr(dataframe_filename, df_bytes)
        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    @classmethod
    def deserialise_from_zip(cls, zip_bytes: bytes) -> "GridManager":
        """
        Reconstruct GridManager from zip_bytes
        """
        instance = cls.__new__(cls)
        with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zip_file:
            # Read manifest
            manager_data = json.loads(zip_file.read("manager_info.json").decode())
            instance.requires_sync=True
            instance.all_hours = manager_data["all_hours"]
            instance.existing_names = {
                k: set(v) for k, v in manager_data["existing_names"].items()
            }
            instance.all_grids = {}

            for key in manager_data["handler_keys"]:
                folder = key.replace(":", "_")
                metadata_filename = f"handlers/{folder}/metadata.json"
                df_parquet_filename = f"handlers/{folder}/dataframe.parquet"
                metadata_json = json.loads(zip_file.read(metadata_filename).decode())
                df_bytes = zip_file.read(df_parquet_filename)
                handler_instance = GridHandler.deserialise_from_storage(
                    metadata_json, df_bytes
                )
                key.replace("_", ":")
                instance.all_grids[key] = handler_instance
        return instance
