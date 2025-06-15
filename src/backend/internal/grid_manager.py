import pandas as pd
from bitarray import bitarray
from src.backend.internal.grid_handler import GridHandler
import src.backend.internal.time_blocks as htb


class GridManager:
    """
    Manages all GridHandler Instances
    """

    def __init__(self):
        self.all_grids = {}
        self.setup_grid_handlers()
        self.existing_names = {"DAY1": set(), "DAY2": set(), "DAY3": set()}

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

    def get_all_hours(self) -> dict:
        """
        Compute the total hours for each person across all grids
        """
        hour_data = {}
        for name_set in self.existing_names.values():
            for name in name_set:
                if name not in hour_data:
                    hour_data[name] = [0, 0, 0]
        for grid_handler in self.all_grids.values():
            hours = grid_handler.get_hours()

            for name, hours in hours.items():
                hour_data[name][grid_handler.day - 1] += hours

        return hour_data


if __name__ == "__main__":
    test = GridManager()

    df1 = test.all_grids["DAY1:MCC"].data
    df2 = test.all_grids["DAY1:HCC1"].data
    df3 = test.all_grids["DAY1:HCC2"].data
    result = test.format_keys_v2(df1, df2, df3)
    print(result)
