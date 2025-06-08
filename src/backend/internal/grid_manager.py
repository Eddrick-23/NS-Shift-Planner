from src.backend.internal.grid_handler import GridHandler


class GridManager:
    """
    Manages all GridHandler Instances
    """

    def __init__(self):
        self.all_grids = []
        self.setup_grid_handlers()

    def setup_grid_handlers(self):
        """
        Set up required grid_handler class instances

        This method is called automatically upon class instantiation
        """
        all_locations = ["MCC ", "HCC1", "HCC2"]
        for location in all_locations:
            for i in range(1, 4):
                if i == 3 and location != "MCC ":
                    continue
                self.all_grids.append(GridHandler(location=location, day=i))

    def format_keys(self, df1, df2=None, df3=None) -> list[str]:
        """
        Aligns timeblocks across 3 dataframes based on identical scheduling.

        This function reads two pandas DataFrames representing timeblock schedules
        and returns a list of formatted time keys and a corresponding list indicating
        whether consecutive blocks can be joined.

        Two consecutive timeblocks can be joined if, for all columns except "DAY" and "Time",
        their values are either both empty or exactly the same (i.e., allocated to the same person).

        Args:
            df1 (pd.DataFrame): The first schedule dataframe.
            df2 (pd.DataFrame): The second schedule dataframe. Can be None.
            df3 (pd.DataFrame): The third schedule dataframe. Can be None.


        Returns:
            list[str]: A list where:
                - each element is a time block that can be combined to a 1h block (e.g. "08:30", can be combined with "08:00")
                - the elements will always be the second half of the hour "xx:30"
        """
        joined_df = df1
        if df2 is not None:
            joined_df = joined_df.merge(df2)
        if df3 is not None:
            joined_df = joined_df.merge(df3)
        blocks_to_remove = []

        # iterate through pairs of rows
        for i in range(0, len(joined_df), 2):
            rows = joined_df.iloc[i : i + 2]
            # check if every row contains identical values
            can_join = True
            for c in rows.columns[2:]:
                v1, v2 = rows[c].iloc[0], rows[c].iloc[1]

                if v1 != v2:
                    can_join = False
                    break
            if can_join:
                blocks_to_remove.append(
                    rows.Time.iloc[1]
                )  # slice string for HH:MM format

        return blocks_to_remove


if __name__ == "__main__":
    test = GridManager()
    test.setup_grid_handlers()

    print(len(test.all_grids))
