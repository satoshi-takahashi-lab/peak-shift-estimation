import student_generator
import admission_judge
import shutil

if __name__ == "__main__":
    shutil.rmtree("example_data", ignore_errors=True)
    student_generator.main()
    admission_judge.main()
