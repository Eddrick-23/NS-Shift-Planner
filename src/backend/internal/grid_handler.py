import pandas as pd
from typing import Literal
import logging


class GridHandler:
    """
    custom batabase for streamlit front end.
    Database stores allocated shift for each person by day
    """

    def __init__(
        self,
        location: Literal["MCC", "HCC1", "HCC2"],
        day: int,
        use_default=True,
        data=None,
    ):
        """
        Initializes the daily grid for a specific location and day.

        Args:
            location: The location of the mount (e.g., "MCC", "HCC1", "HCC2").
            day: The day number (1 or 2). Day 2 affects timeblock indexing, starting from 0600.
            use_default: If True, attempts to load default data.
            data: Optional pre-existing data to use if `use_default` is False.
        """
        self.names = set()  # names in this days data base
        self.location = location
        self.day = day
        self.identifier = f"{self.day},{self.location} GridHanlder"
        self.logger = logging.getLogger(__name__)
        self.hours = {}  # stores hour data in name:hour format
        if use_default:
            self.load_data()
        else:
            self.data = data

    def load_data(self):
        """
        loads the raw format for the grid
        """
        df = pd.read_csv("src/backend/internal/raw.csv")
        df = df[df["DAY"] == self.day]
        df = df.reset_index(drop=True)
        self.data = df

    def set_data(self, data):
        """
        Method is called when loading previously stored data
        ====================================================
        data(pandas dataframe object):
            Previously stored dataframe
        """
        self.data = data
        self.names = set(data.columns[2:].tolist())
        # update the hours

        if len(self.names) == 0:
            pass

        else:
            for c in self.data.columns[2:]:  # for each column
                total_hours = 0
                freq = self.data[c].value_counts().to_dict()
                if "MCC" in freq:
                    total_hours += freq["MCC"] * 0.5
                if "HCC1" in freq:
                    total_hours += freq["HCC1"] * 0.5
                if "HCC2" in freq:
                    total_hours += freq["HCC2"] * 0.5

                self.hours[c] = total_hours

    def get_names(self):
        return self.names.copy()

    def name_exists(self, name):
        return name in self.names

    def add_name(self, name, shifts=[]):
        """
        Add a name to the database
            name(str):
                Name will be formatted to upper case
            shifts(list)[optional]:
                List of preallocated shifts from undo/redo calls
            hours(int)[optional]:
                hours allocated for the person
        """
        upper_name = name.upper()
        if self.name_exists(upper_name):
            self.logger.warning(
                "%s:{self.day},Name already exists:%s", self.identifier, self.names
            )
            return
        self.names.add(upper_name)
        if shifts == []:
            self.data[upper_name] = ["0"] * len(
                self.data.index
            )  # each cell is 4 characters long
        else:
            self.data[upper_name] = shifts
        self.hours[upper_name] = self._compute_hours(shifts)

    def _compute_hours(self, shifts: list):
        hours = 0
        for shift in shifts:
            if shift != "0":
                hours += 0.5

        return hours

    def remove_name(self, name):
        """
        name(str):
            Name will be formatted to upper case
        """
        upper_name = name.upper()
        if not self.name_exists(upper_name):
            self.logger.warning(
                "%s:{self.day},{upper_name} does not exist. Existing names: %s",
                self.identifier,
                self.names,
            )
            return
        d = self.data[upper_name].to_list()
        self.data.drop(upper_name, axis=1, inplace=True)
        self.names.remove(upper_name)
        h = self.hours[name]
        del self.hours[name]
        return {"data": d, "hours": h}

    def rename(self, new_name, old_name):
        """
        Method is used when swapping names between databases/renaming column names
        ==========================================================================
        new_name(str):
            New name. Name will be formatted to upper case. Name must not currently exist
        old_name(str):
            Old name. Name will be formatted to upper case. Name must not currently exist

        """
        if new_name in self.names:
            self.logger.info("%s:New name %s already exists", self.identifier, new_name)
            return
        if old_name not in self.names:
            self.logger.info(
                "%s:Old name %s does not exist in database", self.identifier, old_name
            )
            return

        # update database column name
        self.data = self.data.rename(columns={old_name: new_name})

        # update the name hour_count
        self.hours[new_name] = self.hours.pop(old_name)
        # update the name set
        self.names.remove(old_name)
        self.names.add(new_name)

    def swap_names(self, name1, name2):
        """
        swaps the names of two existing columns in the database
        """
        if name1 not in self.names:
            self.logger.info("%s:%s does not exist in grid", self.identifier, name1)
            return
        if name2 not in self.names:
            self.logger.info("%s:%s does not exist in grid", self.identifier, name2)
            return
        self.data = self.data.rename(columns={name1: name2, name2: name1})
        self.hours[name1], self.hours[name2] = (
            self.hours[name2],
            self.hours[name1],
        )  # swap the hour count

    def is_shift_allocated(self, time_block, name) -> bool | None:
        """
        time_block(str):
            str in "HH:MM" Format. In 30 min intervals

        name(str):
            name of person. Must already exist in column
        """
        name_upper = name.upper()
        if name_upper not in self.data.columns:
            self.logger.warning(
                "%s:%s does not exist in the grid", self.identifier, name
            )
            return None
        rows = self.data[self.data.Time == time_block]
        if rows.empty:
            self.logger.warning(
                "%s:%s is not a valid time block", self.identifier, time_block
            )
            return None
        return rows[name_upper].iloc[0] != "0"

    def allocate_shift(self, location, time_block, name):
        """
        Allocate a shift to a person at a specified time_block and location

        Args:
            location(str):
                "MCC" or "HCC1" or "HCC2"
            time_block(str):
                str in "HH:MM" Format. In 30 min intervals
            name(str):
                name of person. Must already exist in column
        """
        # shift empty add hours
        # shift changing to "0" subtract hours
        # shift replacing to different location, keep hours change location
        final_location, allocated = self._resolve_location(location, time_block, name)
        if final_location is None:
            return
        if not allocated:
            self.hours[name] += 0.5
        elif allocated and final_location == "0":
            self.hours[name] -= 0.5
        self.data.loc[(self.data.Time == time_block), name.upper()] = final_location

    def _resolve_location(
        self, new_location: str, time_block: str, name: str
    ) -> tuple[str | None, bool]:
        """
        Resolve the final location to allocate
        - If location == current location, we deallocate
        - If location != "0" we allocate

        Args:
            location(str): location to allocate
            time_block(str): time block to allocate
            name(str): name to allocate to

        Returns:
            - final allocation location(str)| (None) if there is internal error
            - Whether current block is already allocated(bool)
        """
        final_location = new_location
        # check if shift is currently allocated
        allocated = self.is_shift_allocated(time_block, name)
        if allocated is None:
            return None, False

        # For day 3 location should be "MCC" or "0"
        if self.day == 3 and new_location not in ["MCC", "0"]:
            final_location = "MCC"  # default location for night duty

        # get the current location
        current_location = self.get_shift_location(time_block, name)
        if current_location is None:
            return None, False

        if current_location == final_location:
            final_location = "0"
        return final_location, allocated

    def remove_shift(self, time_block, name):
        """
        time_block(str):
            str in "HH:MM" Format. In 30 min intervals
        name(str):
            name of person. Must already exist in column
        """
        self.data.loc[(self.data.Time == time_block), name.upper()] = "0"
        self.hours[name] -= 0.5

    def get_shift_location(self, time_block, name):
        """
        time_block(str):
            str in "HH:MM:SS" Format. In 30 min intervals
        name(str):
            name of person. Must already exist in column
        """
        name_upper = name.upper()
        if name_upper not in self.data.columns:
            self.logger.warning(
                "%s:%s does not exist in the grid", self.identifier, name
            )
            return None
        rows = self.data[self.data.Time == time_block]
        if rows.empty:
            self.logger.warning(
                "%s:%s is not a valid time block", self.identifier, time_block
            )
            return None

        return rows[name_upper].iloc[0]

    def check_lunch_and_dinner(self):
        """
        Returns names of people who do not have a lunch or dinner break
        """
        # checks if someone has no lunch/dinner break.
        # names will be returned in an array

        # lunch  = 1130-1330 >> I.e. cannot start from 1100 and end at 1330 without break
        # dinner = 1700-1830 >> cannot start at 1700 and end at 1830 without break
        result = set()  # stores names who don't have breaks
        lunch = self.data[
            (self.data["Time"] >= "11:00") & (self.data["Time"] <= "13:00")
        ]
        dinner = self.data[
            (self.data["Time"] >= "17:00") & (self.data["Time"] <= "18:00")
        ]

        for c in lunch.columns[2:]:  # check lunch
            if "0" not in lunch[c].array:
                result.add(c)
        for c in dinner.columns[2:]:  # check dinner
            if c not in result and "0" not in dinner[c].array:
                result.add(c)

        return result

    def generate_formatted_dataframe(self, blocks_to_remove):
        """
        Formats the dataframe to the required format for the front end, including the 1h time blocks that can be joined
        """
        data = self.data.copy()
        data = data.drop(columns=["DAY"])
        rotated_df = data.set_index("Time").T.reset_index()

        rotated_df = rotated_df.rename(
            columns={"index": f"DAY{self.day}:{self.location}"}
        )
        rotated_df = rotated_df.drop(columns=blocks_to_remove)

        return rotated_df

    def df_to_aggrid_format(self, df):
        """
        Converts dataframe to aggrid supported format

        Returns:
            list[dict]:
                list of dictionaries to be served as json data for frontend
        """
        # Create column definitions (skip index if needed)
        column_defs = [{"headerName": col, "field": col} for col in df.columns]
        # Add styling for first column
        self._style_columns(column_defs)

        # Convert dataframe rows to list of dicts
        row_data = df.to_dict(orient="records")
        # Add styling for row_data

        return {
            "columnDefs": column_defs,
            "rowData": row_data,
        }

    def _style_columns(self, column_defs: list[dict]) -> list[dict]:
        """
        Inject data into column definitions for styling
        """
        # fix first column width
        column_defs[0]["width"] = 150
        column_defs[0]["suppressSizeToFit"] = True  # fix column width
        # add flex to rest of columns and cell calss rules
        cell_class_rules = {
            "bg-white text-white": 'x=="0"',
            "bg-green text-green": f'x=="{self.location}"',
            "bg-green text-black": f'x != 0 && x !=="{self.location}"'
        }
        for i in range(1, len(column_defs)):
            data = column_defs[i]
            data["flex"] = 1
            data["resizable"] = False
            data["sortable"] = False
            data["cellClassRules"] = cell_class_rules
        return column_defs

    def store_json(self):
        """
        Convert dataframe to json for storage in database
        """
        data = self.data.copy()
        json_data = data.to_json()

        return json_data
