import math
from numpy.random import default_rng
import random
import pandas as pd
import scipy.stats as stats
import os
from decimal import Decimal, ROUND_HALF_UP
import shutil


NUM_OF_ALL_STUDENTS = 100 * 1000
AVE_ABILTY_OF_ALL_STUDENTS = 0
STD_ABILTY_OF_ALL_STUDENTS = 1
NUM_OF_HIGHSCHOOLS = 1000
AVE_ABILTY_BETWEEN_HIGHSCHOOLS = 0
RADIAN = 45
STD_ABILTY_BETWEEN_HIGHSCHOOLS = math.sin(math.radians(RADIAN))
STD_ABILTY_WITHIN_HIGHSCHOOL = math.cos(math.radians(RADIAN))
UPEER_THRESH_STD_ABILTY_WITHIN_HIGHSCHOOL = STD_ABILTY_WITHIN_HIGHSCHOOL + 1.96 * 0.2
LOWWER_THRESH_STD_ABILTY_WITHIN_HIGHSCHOOL = STD_ABILTY_WITHIN_HIGHSCHOOL - 1.96 * 0.2
LOOP_MAX = 1000

RG = default_rng(0)
random.seed(0)
OUTPUT_DIR = "example_data/"
STUDENT_ABILTY_PATH = "student_abilty.csv"


def make_output_dir():
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def get_each_num_of_students_in_each_highschool_list():
    # Generate a uniform number of students at each high school.
    each_num_of_students_in_each_highschool_list = [
        int(NUM_OF_ALL_STUDENTS / NUM_OF_HIGHSCHOOLS) for _ in range(NUM_OF_HIGHSCHOOLS)
    ]
    return each_num_of_students_in_each_highschool_list


def get_each_ave_ability_within_highschool_list():
    count = 0
    stats_thresh = 0.787
    anderson_stats = 1
    # Check if the generated list is normal distribution.
    while anderson_stats > stats_thresh:
        each_ave_ability_within_highschool_list = RG.normal(
            AVE_ABILTY_BETWEEN_HIGHSCHOOLS,
            STD_ABILTY_BETWEEN_HIGHSCHOOLS,
            NUM_OF_HIGHSCHOOLS,
        )
        anderson_stats, _, _ = stats.anderson(
            each_ave_ability_within_highschool_list, dist="norm"
        )
        count += 1
        if count == 10000:
            print("Cannot generate each_ave_ability_within_highschool_list")
            break

    return each_ave_ability_within_highschool_list


def get_ablity_of_all_students_list():
    count = 0
    stats_thresh = 0.787
    anderson_stats = 1
    # Check if the generated list is normal distribution.
    while anderson_stats > stats_thresh:
        ablity_of_all_students_list = RG.normal(
            AVE_ABILTY_OF_ALL_STUDENTS,
            STD_ABILTY_OF_ALL_STUDENTS,
            NUM_OF_ALL_STUDENTS,
        )
        anderson_stats, _, _ = stats.anderson(ablity_of_all_students_list, dist="norm")
        count += 1
        if count == 10000:
            print("Cannot generate ablity_of_all_students_list")
            break
    return ablity_of_all_students_list


def choose_highschool_based_on_stundent_ability(
    student_ability,
    probability_of_belonging_to_each_highschool_df,
    each_num_of_highschool_students_under_calculation_list,
    each_num_of_highschool_students_list,
    each_ave_ability_within_highschool_list,
):
    highschool_list = list(range(NUM_OF_HIGHSCHOOLS))
    weights = list(
        probability_of_belonging_to_each_highschool_df.loc[
            float(Decimal(student_ability).quantize(Decimal("0.1"), ROUND_HALF_UP))
        ]
    )
    chosen_highschool = random.choices(highschool_list, k=1, weights=weights)[0]
    # When the number of students in the high school is exceeded,
    # choose the one with the smallest difference from the average within the high school
    if (
        each_num_of_highschool_students_under_calculation_list[chosen_highschool]
        >= each_num_of_highschool_students_list[chosen_highschool]
    ):
        remaining_highschool_list = [
            i
            for i in range(NUM_OF_HIGHSCHOOLS)
            if each_num_of_highschool_students_under_calculation_list[i]
            < each_num_of_highschool_students_list[i]
        ]
        difference_in_abilities_between_remained_and_chosen_highschool_list = [
            abs(
                each_ave_ability_within_highschool_list[i]
                - each_ave_ability_within_highschool_list[chosen_highschool]
            )
            for i in remaining_highschool_list
        ]
        chosen_highschool = remaining_highschool_list[
            difference_in_abilities_between_remained_and_chosen_highschool_list.index(
                min(difference_in_abilities_between_remained_and_chosen_highschool_list)
            )
        ]

    return chosen_highschool


def check_limitation_of_num_of_highschool_students(
    probability_of_belonging_to_each_highschool_df,
    each_num_of_highschool_students_under_calculation_list,
    chosen_highschool,
    each_num_of_highschool_students_list,
):
    # When the number of students in the high school is exceeded,
    # set the probability to 0
    each_num_of_highschool_students_under_calculation_list[chosen_highschool] += 1
    if (
        each_num_of_highschool_students_under_calculation_list[chosen_highschool]
        >= each_num_of_highschool_students_list[chosen_highschool]
    ):
        probability_of_belonging_to_each_highschool_df[chosen_highschool] = 0.0
    return (
        probability_of_belonging_to_each_highschool_df,
        each_num_of_highschool_students_under_calculation_list,
    )


def get_probability_of_belonging_to_each_highschool_df(
    ablity_of_all_students_list, each_ave_ability_within_highschool_list
):
    def round_half_up(n):
        return float(Decimal(n).quantize(Decimal("0.1"), ROUND_HALF_UP))

    student_ability_set = list(set(map(round_half_up, ablity_of_all_students_list)))

    probability_of_belonging_to_each_highschool_df = pd.DataFrame(
        index=student_ability_set, columns=list(range(NUM_OF_HIGHSCHOOLS))
    )
    for ability in student_ability_set:
        for highschool in list(range(NUM_OF_HIGHSCHOOLS)):
            probability_of_belonging_to_each_highschool_df.at[
                ability, highschool
            ] = stats.norm.pdf(
                x=ability,
                loc=each_ave_ability_within_highschool_list[highschool],
                scale=STD_ABILTY_WITHIN_HIGHSCHOOL,
            )
    return probability_of_belonging_to_each_highschool_df


def rename_highschool(df):
    # highschool_000 has high average abilty.
    ave_ability_within_highschool_df = pd.DataFrame(
        {
            "ave_ability_within_highschool": df.groupby("highschool")
            .mean()
            .student_ablity
        }
    )
    ave_ability_within_highschool_df = ave_ability_within_highschool_df.sort_values(
        "ave_ability_within_highschool", ascending=False
    )
    ave_ability_within_highschool_dict = dict(
        zip(
            ave_ability_within_highschool_df.index,
            [
                "highschool_" + str(i).zfill(3)
                for i in range(len(ave_ability_within_highschool_df))
            ],
        )
    )
    df["highschool"] = df["highschool"].map(ave_ability_within_highschool_dict)

    return df


def is_all_highschool_within_std_score_thresh(df):
    std_ability_within_highschool_df = pd.DataFrame(
        {"std_abilty_within_highschool": df.groupby("highschool").std().student_ablity}
    )
    num_of_highschool_over_std_score_thresh = len(
        std_ability_within_highschool_df[
            std_ability_within_highschool_df["std_abilty_within_highschool"]
            > UPEER_THRESH_STD_ABILTY_WITHIN_HIGHSCHOOL
        ]
    )
    num_of_highschool_under_high_std_score_thresh = len(
        std_ability_within_highschool_df[
            std_ability_within_highschool_df["std_abilty_within_highschool"]
            < LOWWER_THRESH_STD_ABILTY_WITHIN_HIGHSCHOOL
        ]
    )
    print(
        "num_of_highschool_over_std_score_thresh:"
        + str(num_of_highschool_over_std_score_thresh)
    )
    print(
        "num_of_highschool_under_high_std_score_thresh:"
        + str(num_of_highschool_under_high_std_score_thresh)
    )
    return (num_of_highschool_over_std_score_thresh < 1) & (
        num_of_highschool_under_high_std_score_thresh < 1
    )


def main():
    make_output_dir()
    for error_count in range(LOOP_MAX):
        print("error_count:{}".format(error_count))
        each_num_of_students_in_each_highschool_list = (
            get_each_num_of_students_in_each_highschool_list().copy()
        )
        each_ave_ability_within_highschool_list = (
            get_each_ave_ability_within_highschool_list().copy()
        )
        ablity_of_all_students_list = get_ablity_of_all_students_list().copy()

        highschool_for_each_student_list = [-1] * NUM_OF_ALL_STUDENTS
        each_num_of_highschool_students_under_calculation_list = [
            0
        ] * NUM_OF_HIGHSCHOOLS
        probability_of_belonging_to_each_highschool_df = (
            get_probability_of_belonging_to_each_highschool_df(
                ablity_of_all_students_list.copy(),
                each_ave_ability_within_highschool_list.copy(),
            )
        )

        for student in range(NUM_OF_ALL_STUDENTS):
            chosen_highschool = choose_highschool_based_on_stundent_ability(
                ablity_of_all_students_list[student].copy(),
                probability_of_belonging_to_each_highschool_df.copy(),
                each_num_of_highschool_students_under_calculation_list.copy(),
                each_num_of_students_in_each_highschool_list.copy(),
                each_ave_ability_within_highschool_list.copy(),
            )
            highschool_for_each_student_list[student] = chosen_highschool
            (
                probability_of_belonging_to_each_highschool_df,
                each_num_of_highschool_students_under_calculation_list,
            ) = check_limitation_of_num_of_highschool_students(
                probability_of_belonging_to_each_highschool_df.copy(),
                each_num_of_highschool_students_under_calculation_list.copy(),
                chosen_highschool,
                each_num_of_students_in_each_highschool_list.copy(),
            )
        stundent_ability_df = pd.DataFrame(
            {
                "highschool": highschool_for_each_student_list,
                "student_ablity": ablity_of_all_students_list,
            }
        )

        stundent_ability_df = rename_highschool(stundent_ability_df)

        if is_all_highschool_within_std_score_thresh(stundent_ability_df):
            stundent_ability_df.to_csv(os.path.join(OUTPUT_DIR, STUDENT_ABILTY_PATH))
            break


if __name__ == "__main__":
    main()
