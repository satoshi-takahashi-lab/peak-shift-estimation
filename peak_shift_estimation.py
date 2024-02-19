import os
import pandas as pd
from pyclustering.cluster import xmeans
import numpy as np
import random
from scipy.stats import pearsonr
import math
import sys as Sys


INPUT_DIR = "./result"
SUCCESSFUL_RATE_PATH = "successful_rate.csv"
OUTPUT_DIR = "./result"
TEMPORARY_RANKING_IN_EACH_CALCULATION_PATH = "temporary_ranking_in_each_calculation.csv"
ESTIMATED_RESULT_RANKING_PATH = "estimated_ranking.csv"

CALCULATION_TIME_OF_EACH_UNIVERSITY = 10


def replace_university_positions(input_df, fixed_university_list):
    input_university_list = input_df.columns.tolist()
    not_fixed_university_list = list(
        set(input_university_list) - set(fixed_university_list)
    )
    replaced_university_list = fixed_university_list + not_fixed_university_list
    university_replaced_input_df = input_df.loc[:, replaced_university_list]
    return university_replaced_input_df


def replace_highschool_positions(input_df, fixed_highschool_list):
    input_highschool_list = input_df.index.tolist()
    not_fixed_highschool_list = list(
        set(input_highschool_list) - set(fixed_highschool_list)
    )
    replaced_highschool_list = fixed_highschool_list + not_fixed_highschool_list
    highschool_replaced_input_df = input_df.loc[replaced_highschool_list, :]
    return highschool_replaced_input_df


def detect_top_universities(input_df, fixed_highschool_list, fixed_university_list):
    # Extract the number of accepted students who are not on the fixed_university_list and on the fixed_highschool_list.
    fixed_highschool_input_df = input_df.loc[fixed_highschool_list, :]
    fixed_highschool_university_input_df = fixed_highschool_input_df.iloc[
        :, len(fixed_university_list) :
    ]

    if len(fixed_highschool_university_input_df.columns) < 2:
        return fixed_highschool_university_input_df.columns.tolist()

    # Remove universities with no accepted students.
    university_with_even_one_accepted_student_list = []
    for i in fixed_highschool_university_input_df.columns:
        if sum(fixed_highschool_university_input_df.loc[:, i]) > 0:
            university_with_even_one_accepted_student_list.append(i)
    fixed_highschool_university_input_df = fixed_highschool_university_input_df.loc[
        :, university_with_even_one_accepted_student_list
    ]

    # Cluster universities based on the number of accepted students.
    num_of_accepted_students_list = (
        fixed_highschool_university_input_df.T.values.tolist()
    )
    university_list = fixed_highschool_university_input_df.columns.tolist()

    # If there is only one university, return it.
    if len(university_list) == 1:
        return university_list

    try:
        init_center = xmeans.kmeans_plusplus_initializer(
            data=num_of_accepted_students_list, amount_centers=2, random_state=0
        ).initialize()
    except ValueError as e:
        # If two clusters cannot be created
        print(e)
        return university_list

    xm = xmeans.xmeans(
        data=num_of_accepted_students_list, initial_centers=init_center, ccore=True
    )
    xm.process()
    university_clusters = xm.get_clusters()

    # Define universities with the highest average number of accepted applicants as top universities.
    average_num_of_accepted_students_list = []
    for cluster in university_clusters:
        total_num_of_accepted_students = 0
        for university in cluster:
            total_num_of_accepted_students += sum(
                num_of_accepted_students_list[university]
            )
        average_num_of_accepted_students_list.append(
            total_num_of_accepted_students / len(cluster)
        )

    max_index = np.argmax(average_num_of_accepted_students_list)
    detected_top_university_list = []
    for university in university_clusters[max_index]:
        detected_top_university_list.append(university_list[university])
    return detected_top_university_list


def main_funcion(params):
    (
        input_df,
        num_of_highschools_per_num_of_universities,
        fixed_university_list,
        each_step_fixed_university_list,
        fixed_highschool_list,
        univercity_list,
    ) = params

    # Sort high schools by the number of accepted_students fixed_university_list
    num_of_accepted_students_each_high_school_df = (
        input_df[fixed_university_list].sum(axis="columns").sort_values(ascending=False)
    )

    # Add top high schools to fixed_highschool_list.
    num_of_high_schools_to_extract = int(
        len(fixed_university_list) * num_of_highschools_per_num_of_universities
    )
    fixed_highschool_list.extend(
        num_of_accepted_students_each_high_school_df.index[
            :num_of_high_schools_to_extract
        ]
    )

    # Replace the top high schools to the top
    input_df = replace_highschool_positions(
        input_df.copy(), fixed_highschool_list.copy()
    )

    while len(fixed_university_list) < len(input_df.columns):
        # Detect top universities
        detected_top_university_list = detect_top_universities(
            input_df.copy(),
            fixed_highschool_list.copy(),
            fixed_university_list.copy(),
        )
        fixed_university_list.extend(detected_top_university_list.copy())
        each_step_fixed_university_list.append(detected_top_university_list.copy())

        # Replace the top universities to the left
        input_df = replace_university_positions(
            input_df.copy(), fixed_university_list.copy()
        )

        # Sort high schools by the number of accepted students of detected top universities
        sorted_by_accepted_students_input_df = (
            input_df[fixed_university_list]
            .sum(axis="columns")
            .sort_values(ascending=False)
        )

        # Add top high schools to fixed_highschool_list.
        for high_school in sorted_by_accepted_students_input_df.index:
            if len(fixed_highschool_list) > int(
                len(fixed_university_list) * num_of_highschools_per_num_of_universities
            ):
                break

            if high_school not in fixed_highschool_list:
                fixed_highschool_list.append(high_school)

        # Replace the top high schools to the top
        input_df = replace_highschool_positions(
            input_df.copy(),
            fixed_highschool_list.copy(),
        )

    result_rank_list = [""] * len(univercity_list)
    rank = 1
    for university_cluser in each_step_fixed_university_list:
        for university in university_cluser:
            result_rank_list[univercity_list.index(university)] = rank
        rank += len(university_cluser)

    return result_rank_list


def init_output_dir() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def calc_p_hit(num_of_university, num_of_divisions=100, p_threshold=0.99):
    for i in range(1, num_of_divisions):
        extract_rate = i / num_of_divisions
        num_of_extracted_university = int(num_of_university * extract_rate)
        p_not_hit = math.comb(
            num_of_university - num_of_extracted_university, num_of_extracted_university
        ) / math.comb(num_of_university, num_of_extracted_university)
        p_hit = 1 - p_not_hit
        p_all_hit = p_hit ** math.comb(CALCULATION_TIME_OF_EACH_UNIVERSITY, 2)
        if p_all_hit > p_threshold:
            return extract_rate

    Sys.exit("Error: p_hit is not found.")


def main():
    init_output_dir()

    input_df = pd.read_csv(
        os.path.join(INPUT_DIR, SUCCESSFUL_RATE_PATH), header=0, index_col="highschool"
    )

    # Delete universities with a total of 0 accepted students.
    input_sum_df = input_df.sum()
    input_df = input_df.drop(input_sum_df[input_sum_df == 0].index, axis=1)

    all_university_list = input_df.columns.tolist()
    extract_rate = calc_p_hit(len(all_university_list))

    max_mean_pearsonr = 0
    university_rank_df = []

    for first_fixed_university in all_university_list:
        result = []
        result_df = pd.DataFrame(index=input_df.columns.tolist())

        for calculation_count in range(CALCULATION_TIME_OF_EACH_UNIVERSITY):
            np.random.seed(calculation_count)
            random.seed(calculation_count)
            print(
                "first_fixed_university: "
                + first_fixed_university
                + " calculation_count: "
                + str(calculation_count)
            )

            input_temp_df = input_df.copy()

            # Add the temporay top university to the fixed_university_list.
            fixed_university_list = [first_fixed_university]
            each_step_fixed_university_list = [fixed_university_list.copy()]

            # Replace the top universities to the left
            input_temp_df = replace_university_positions(
                input_temp_df.copy(), fixed_university_list.copy()
            )

            # Drop a part of universities without the fixed university.
            drop_university_list = random.sample(
                list(input_temp_df.columns.values)[1:],
                int(len(list(input_temp_df.columns.values)[1:]) * extract_rate),
            )
            input_temp_df = input_temp_df.drop(drop_university_list, axis=1)

            num_of_highschools_per_num_of_universities = len(input_temp_df.index) / len(
                input_temp_df.columns
            )

            # Create a list of university names for ranking records.
            univercity_list = input_temp_df.columns.tolist()

            fixed_highschool_list = []
            params = (
                input_temp_df.copy(),
                num_of_highschools_per_num_of_universities,
                fixed_university_list.copy(),
                each_step_fixed_university_list.copy(),
                fixed_highschool_list.copy(),
                univercity_list.copy(),
            )
            result = main_funcion(params)

            result_temp_df = pd.DataFrame(result, index=univercity_list)
            result_df = pd.concat([result_df, result_temp_df], axis=1)

        # Calculate the pearson correlation coefficient between the rankings of each simulation.
        result_df.columns = ["cal_" + str(i) for i in range(len(result_df.columns))]
        columns_list = result_df.columns.tolist()
        corr_list = []
        for column_num1 in range(0, len(columns_list)):
            for column_num2 in range(column_num1 + 1, len(columns_list)):
                result_temp_df = result_df[
                    [columns_list[column_num1], columns_list[column_num2]]
                ]
                result_temp_df = result_temp_df.dropna()
                corr, calculation_count = pearsonr(
                    result_temp_df[columns_list[column_num1]],
                    result_temp_df[columns_list[column_num2]],
                )
                corr_list.append(corr)
        temp_mean_pearsonr = np.mean(corr_list)

        if temp_mean_pearsonr > max_mean_pearsonr:
            max_mean_pearsonr = temp_mean_pearsonr
            candidate_result_df = result_df.copy()

    candidate_result_df.to_csv(
        os.path.join(OUTPUT_DIR, TEMPORARY_RANKING_IN_EACH_CALCULATION_PATH)
    )
    candidate_result_df.index.name = "university"
    candidate_result_ave_df = candidate_result_df.mean(axis="columns")

    university_rank_df = candidate_result_ave_df.rank(method="min")
    university_rank_df = university_rank_df.rename("rank")
    university_rank_df = university_rank_df.astype("int64")
    university_rank_df.index.name = "university"
    university_rank_df.to_csv(os.path.join(OUTPUT_DIR, ESTIMATED_RESULT_RANKING_PATH))


if __name__ == "__main__":
    main()
