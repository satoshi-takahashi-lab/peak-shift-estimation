import pandas as pd
import os
from numpy.random import default_rng

NUM_OF_UNIVERSITIES = 100
AVE_ABILTY_OF_UNIBERSITIES = 0
STD_ABILTY_OF_UNIBERSITIES = 1
NUM_OF_STUDENTS_IN_UNIBERSITY = 100
UPPER_LIMIT_OF_ABILTY_DIFFERENCE = 1
LOWWER_LIMIT_OF_ABILTY_DIFFERENCE = 1
APPLICATION_FLAG = 1
SUCCESSFUL_FLAG = 2
ENROLLMENT_FLAG = 3

RG = default_rng(0)
INPUT = "./example_data/"
STUDENT_ABILTY_PATH = "student_abilty.csv"
OUTPUT_DIR = "./example_data/"
SUCCESSFUL_PATH = "successful_num.csv"


def generate_university_df():
    abilty_of_university_list = RG.normal(
        AVE_ABILTY_OF_UNIBERSITIES, STD_ABILTY_OF_UNIBERSITIES, NUM_OF_UNIVERSITIES
    )
    abilty_of_university_list = sorted(abilty_of_university_list, reverse=True)
    num_of_students_in_university_list = [
        NUM_OF_STUDENTS_IN_UNIBERSITY
    ] * NUM_OF_UNIVERSITIES

    university_df = pd.DataFrame(
        index=["university_" + str(i).zfill(2) for i in range(NUM_OF_UNIVERSITIES)]
    )
    university_df["abilty_of_university"] = abilty_of_university_list
    university_df["num_of_students_in_university"] = num_of_students_in_university_list

    return university_df


def generate_highschool_student_df():
    highschool_student_df = pd.read_csv(
        os.path.join(INPUT, STUDENT_ABILTY_PATH), index_col=0
    )
    highschool_student_df = highschool_student_df.sort_values(
        "student_ablity", ascending=False
    )

    return highschool_student_df


def generate_highschool_df(highschool_student_df):
    highschool_df = pd.DataFrame(
        {
            "num_of_students_in_highschool": list(
                highschool_student_df.groupby("highschool").count()["student_ablity"]
            )
        },
        index=list(highschool_student_df.groupby("highschool").count().index),
    )

    return highschool_df


def judge_application(university_df, highschool_student_df):
    for university_name, univerity in university_df.iterrows():
        applicant_index = highschool_student_df[
            (
                highschool_student_df["student_ablity"]
                > univerity["abilty_of_university"] - LOWWER_LIMIT_OF_ABILTY_DIFFERENCE
            )
            & (
                highschool_student_df["student_ablity"]
                < univerity["abilty_of_university"] + UPPER_LIMIT_OF_ABILTY_DIFFERENCE
            )
        ].index
        highschool_student_df.loc[applicant_index, university_name] = APPLICATION_FLAG

    return highschool_student_df


def judge_enrollment(university_df, highschool_student_df):
    highschool_student_df["enrollment_checker"] = 0
    for university_name, university in university_df.iterrows():
        num_of_students_in_university = university["num_of_students_in_university"]
        total_num_of_students_enrolled = 0
        applicant_name_index = highschool_student_df[
            highschool_student_df[university_name] == APPLICATION_FLAG
        ].index
        for applicant_name in applicant_name_index:
            if total_num_of_students_enrolled >= num_of_students_in_university:
                break
            # Applicants who are not already enrolled in any university.
            if (
                highschool_student_df.at[applicant_name, "enrollment_checker"] != 1
                and highschool_student_df.at[applicant_name, university_name]
                == APPLICATION_FLAG
            ):
                highschool_student_df.at[applicant_name, "enrollment_checker"] = 1
                highschool_student_df.at[
                    applicant_name, university_name
                ] = ENROLLMENT_FLAG
                total_num_of_students_enrolled += 1
    highschool_student_df = highschool_student_df.drop("enrollment_checker", axis=1)

    return highschool_student_df


def judge_successful(university_df, highschool_student_df):
    for university_name in university_df.index:
        applicant_name_index = highschool_student_df[
            highschool_student_df[university_name] >= APPLICATION_FLAG
        ].index
        for applicant_name in applicant_name_index:
            if (
                highschool_student_df.at[applicant_name, university_name]
                == ENROLLMENT_FLAG
            ):
                break
            else:
                highschool_student_df.at[
                    applicant_name, university_name
                ] = SUCCESSFUL_FLAG

    return highschool_student_df


def replace_columns_positions(highschool_student_df):
    input_columns_list = highschool_student_df.columns.tolist()
    input_columns_list.remove("num_of_students_in_highschool")
    input_columns_list.remove("highschool")
    input_columns_list = [
        "highschool",
        "num_of_students_in_highschool",
    ] + input_columns_list
    highschool_student_df = highschool_student_df.loc[:, input_columns_list]
    return highschool_student_df


def generate_successful_rate_df(highschool_student_df, highschool_df):
    successful_df = highschool_student_df.loc[:, "university_00":]
    successful_df = successful_df.replace(APPLICATION_FLAG, 0)
    successful_df = successful_df.replace(SUCCESSFUL_FLAG, 1)
    successful_df = successful_df.replace(ENROLLMENT_FLAG, 1)
    successful_df = pd.concat(
        [highschool_student_df["highschool"], successful_df], axis=1
    )
    grouped_successful_df = successful_df.groupby("highschool").sum()
    grouped_successful_df["num_of_students_in_highschool"] = highschool_df[
        "num_of_students_in_highschool"
    ]

    grouped_successful_df["highschool"] = highschool_df.index
    grouped_successful_df = replace_columns_positions(grouped_successful_df)
    grouped_successful_df.to_csv(os.path.join(OUTPUT_DIR, SUCCESSFUL_PATH), index=False)


def main():
    university_df = generate_university_df()
    highschool_student_df = generate_highschool_student_df()
    highschool_df = generate_highschool_df(highschool_student_df)

    highschool_student_df = judge_application(university_df, highschool_student_df)
    highschool_student_df = judge_enrollment(university_df, highschool_student_df)
    highschool_student_df = judge_successful(university_df, highschool_student_df)

    generate_successful_rate_df(highschool_student_df, highschool_df)


if __name__ == "__main__":
    main()
