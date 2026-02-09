
import pandas as pd
from pathlib import Path
from typing import List, Union

class DataLoader:
    """
    Handles loading and preprocessing of experiment results.
    """
    
    @staticmethod
    def load_experiment_results(file_path: Union[str, Path]) -> pd.DataFrame:
        """
        Load a single experiment result CSV and parse stringified lists.
        """
        df = pd.read_csv(file_path)
        return DataLoader._parse_list_columns(df)

    @staticmethod
    def load_and_merge(file_paths: List[Union[str, Path]]) -> pd.DataFrame:
        """
        Load multiple result files, merge them, and parse stringified lists.
        """
        dfs = [pd.read_csv(fp) for fp in file_paths]
        df = pd.concat(dfs, ignore_index=True)
        return DataLoader._parse_list_columns(df)

    @staticmethod
    def _parse_list_columns(df: pd.DataFrame) -> pd.DataFrame:
        import ast
        for col in df.columns:
            # Check if column looks like a list (starts with [ and ends with ])
            # and is of object type. Or check specific suffixes.
            if df[col].dtype == 'object' and isinstance(df[col].iloc[0], str) and df[col].iloc[0].startswith('[') and df[col].iloc[0].endswith(']'):
                try:
                    df[col] = df[col].apply(ast.literal_eval)
                except (ValueError, SyntaxError):
                    pass
        return df
