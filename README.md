# Peak-Shift-Estimation

## Overview
Peak Shift Estimation (PSE) is a method for estimating the comparative difficulty of exams.<br>
PSE estimates the order of difficulty of the examinations, starting with the most difficult examination, using the institution at which the number of successful candidates peaks as a clue.<br>
The name of this method refers to the way it follows the peak that moves with the difficulty of the exam.<br>
See <a href="https://ieeexplore.ieee.org/document/9678753">Peak Shift Estimation: A Novel Method to Estimate Ranking of Selectively Omitted Examination Data</a> and <br> <a href="https://ieeexplore.ieee.org/document/10286494">Improving Peak Shift Estimation to Rank Exams by Difficulty</a>.<br>

## Usage
To estimate the exam difficulty ranking `python main.py`<br>
See <a href="https://ieeexplore.ieee.org/document/10286494">Improving Peak Shift Estimation to Rank Exams by Difficulty</a> for details of the algorithm.<br>
<br>
To generate example input files `python example_data_generator_main.py` in example_generator directory<br>
See <a href="https://ieeexplore.ieee.org/document/9678753">Peak Shift Estimation: A Novel Method to Estimate Ranking of Selectively Omitted Examination for details of the algorithm.

## Requirements
When you run `main.py`, you need Python 3.11.8 and requirements as below.

```
FIXME
pyclustering==0.10.1.2
pandas==2.2.0
numpy==1.23.2
```

# Note
For ease of understanding, "educational institutions" is described as "high schoools" and "exams" as "universities" (entrance exmas) in the following.

## Setting
### main.py
#### standardizer.py
| Item | Description | Default value |
|:---:|:---:|:---:|
| INPUT_DIR | directory of input files | ./example_data |
| SUCCESSFUL_NUM_PATH | the numbers of sccessful candidates | successful_num.csv |
| OUTPUT_DIR | directory of output files | ./result |
| SUCCESSFUL_RATE_PATH | the standardized numbers of sccessful candidates | successful_rate.csv |

#### peak_shift_estimation.py
| Item | Description | Default value |
|:---:|:---:|:---:|
| INPUT_DIR | directory of input files | ./result |
| SUCCESSFUL_RATE_PATH | standardized numbers of sccessful candidates | successful_rate.csv |
| OUTPUT_DIR | directory of output files | ./result |
| ESTIMATED_RESULT_RANKING_PATH | the estimated exam difficulty ranking | estimated_ranking.csv |
| TEMPORARY_RANKING_IN_EACH_CALCULATION_PATH | the temporary difficulty level ranking in each calculation | temporary_ranking_in_each_calculation.csv |
| CALCULATION_TIME_OF_EACH_UNIVERSITY | calculation time of the temporary difficulty level ranking | 1000 |

### example_data_generator_main.py
#### student_generator.py
| Item | Description | Default value |
|:---:|:---:|:---:|
| OUTPUT_DIR | directory of output files | ./example_data |
| STUDENT_ABILTY_PATH | the abilties of students | student_abilty.csv |

#### admission_judge.py
| Item | Description | Default value |
|:---:|:---:|:---:|
| INPUT_DIR | directory of input files | ./example_data |
| STUDENT_ABILTY_PATH | the abilties of students | student_abilty.csv |
| OUTPUT_DIR | directory of output files | ./example_data |
| SUCCESSFUL_NUM_PATH | the numbers of sccessful candidates | successful_num.csv |

## Inputs and Outputs

### main.py
#### Input files
**<a href="#directory-structure">`successful_num.csv`</a>** (SUCCESSFUL_NUM_PATH) describes the numbers of total candidates in each high shcool and the numbers of sccessful candidates for each university from each high shcool.<br>

```
highschool, num_of_students_in_highschool, university_00, university_01, university_02,,,
highschool_000, 100, 5, 7, 6,,,
highschool_001, 100, 5, 9, 7,,,
highschool_002, 100, 2, 3, 4,,,
highschool_003, 100, 4, 4, 2,,,
highschool_004, 100, 3, 7, 4,,,
```

#### Output files
**<a href="#directory-structure">`estimated_ranking.csv`</a>** (ESTIMATED_RESULT_RANKING_PATH) describes the estimated exam difficulty ranking.<br>
```
university, rank
university_00, 2
university_01, 6
university_02, 2
university_03, 5
university_04, 6
```

**<a href="#directory-structure">`temporary_ranking_each_calculation.csv`</a>** (TEMPORARY_RANKING_IN_EACH_CALCULATION_PATH) describes the temporary difficulty level ranking in each calculation.<br>
```
university, cal_0, cal_1, cal_2, cal_3, cal_4,,,
university_00, , , , , 2.0,,,
university_01, , 3.0, 2.0, 2.0, ,,,
university_02, 4.0, 4.0, , 5.0, ,,,
university_03, 5.0, 3.0, 4.0, 5.0, 7.0,,,
university_04, 7.0, 11.0, 11.0, 9.0, 8.0,,,
```

**<a href="#directory-structure">`successful_rate.csv`</a>** (SUCCESSFUL_RATE_PATH) describes the standardized numbers of sccessful candidates for each university from each high shcool.<br>
```
highschool, university_00, university_01, university_02, university_03, university_04,,,
highschool_000, 0.05, 0.037837838, 0.03, 0.02739726, 0.020771513353115726,,,
highschool_001, 0.05, 0.048648648648648644, 0.035, 0.030821917808219173, 0.026706231,,,
highschool_002, 0.020000000000000004, 0.016216216216216214, 0.02, 0.02739726, 0.026706231,,,
highschool_003, 0.04, 0.021621622, 0.01, 0.01369863, 0.014836795252225518,,,
highschool_004, 0.030000000000000002, 0.037837838, 0.02, 0.020547945205479447, 0.020771513353115726,,,
```

### example_data_generator_main
#### Output files
**<a href="#directory-structure">`student_abilty.csv`</a>** (STUDENT_ABILTY_PATH) describes the students' abilty and highschool.<br>
```
highschool, student_ablity
highschool_869, -1.5286993665128301
highschool_735, -0.747540804077342
highschool_490, 0.3701939910138573
highschool_917, -2.005471161656816
highschool_622, 0.7340038036335875
```

**<a href="#directory-structure">`successful_num.csv`</a>** (SUCCESSFUL_NUM_PATH) describes the numbers of total candidates in each high shcool and the numbers of sccessful candidates for each university from each high shcool.<br>

```
highschool, num_of_students_in_highschool, university_00, university_01, university_02,,,
highschool_000, 100, 5, 7, 6,,,
highschool_001, 200, 5, 9, 7,,,
highschool_002, 150, 2, 3, 4,,,
highschool_003, 130, 4, 4, 2,,,
highschool_004, 170, 3, 7, 4,,,
```

## Directory Structure
```
.
├── main.py
├── peak_shift_estimation.py
├── standardizer.py
├── result
│   ├── successful_rate.csv
│   ├── estimated_ranking.csv
│   └── estimated_ranking_each_calculation.csv
├── example_data
│   ├── student_abilty.csv
│   └── successful_num.csv
└── example_generator
    ├── example_data_generator_main.py
    ├── student_generator.py
    └── admission_judge.py
```

## Author
 
* Satoshi Takahashi, Kanto Gakuin University, satotaka@kanto-gakuin.ac.jp, ORCID: 0000-0002-1067-6704
* Masaki Kitazawa, Kitazawa Tech and Rikkyo University, masaki.kitazawa@rikkyo.ac.jp, ORCID: 0000-0002-6352-0164
* Atsushi Yoshikawa, Kanto Gakuin University, atsuyoshi@kanto-gakuin.ac.jp, ORCID: 0000-0001-7020-508

## License

"Peak-Shift-Estimation" is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).
