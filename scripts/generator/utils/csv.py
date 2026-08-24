import pandas as pd
from pathlib import Path


def write_csv(
    records,
    path: str,
):
    output_path = Path(path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe = pd.DataFrame(
        [
            record.model_dump()
            for record in records
        ]
    )

    dataframe.to_csv(
        output_path,
        index=False,
    )