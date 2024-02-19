import pandas as pd
import os
import shutil

INPUT_DIR = "./example_data/"
SUCCESSFUL_NUM_PATH = "successful_num.csv"

OUTPUT_DIR = "./result/"
SUCCESSFUL_RATE_PATH = "successful_rate.csv"


def main():
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    successful_df = pd.read_csv(
        os.path.join(INPUT_DIR, SUCCESSFUL_NUM_PATH), index_col=0
    )

    # Divide the number of successful applicants by num of graduates, respectively.
    successful_rate_df = successful_df.apply(lambda x: x[1:] / x[0], axis=1)
    # Divide the elements by the column-wise total.
    successful_rate_df = successful_rate_df.apply(lambda x: x / x.sum())

    successful_rate_df.to_csv(os.path.join(OUTPUT_DIR, SUCCESSFUL_RATE_PATH))


if __name__ == "__main__":
    main()
