import mxlit as mt



grade_to_point = {
    "O": 10,
    "A+": 9,
    "A": 8,
    "B+": 7,
    "B": 6,
    "C": 5,
}
grades = list(grade_to_point.keys())


def calculate_cgpa(
    grade_points: list[int],
    credits: list[float],
    previous_cgpa: float = 0,
    previous_credit: float = 0,
):
    total_credit = sum(credit) + previous_credit
    total_grade_points = sum(
        grade_point * credit for grade_point, credit in zip(grade_points, credits)
    ) + (previous_cgpa * previous_credit)
    return total_grade_points / total_credit


mt.title("CGPA Calculator")

mt.markdown(
    "This is a simple CGPA calculator that calculates your CGPA based on your grades and credits"
)

mt.latex(r"CGPA = \frac{\sum_{i=1}^{n} (grade_i * credit_i)}{\sum_{i=1}^{n} credit_i}")
with mt.expander("Grade Table"):
    with mt.html_table(className="w-full"):
        with mt.table_head():
            with mt.table_row():
                with mt.table_cell(header=True, scope="col"): mt.write("Marks")
                with mt.table_cell(header=True, scope="col"): mt.write("Grade")
                with mt.table_cell(header=True, scope="col"): mt.write("Points")
        with mt.table_body():
            with mt.table_row():
                with mt.table_cell(): mt.write("90-100")
                with mt.table_cell(): mt.write("O")
                with mt.table_cell(): mt.write("10")
            with mt.table_row():
                with mt.table_cell(): mt.write("80-89")
                with mt.table_cell(): mt.write("A+")
                with mt.table_cell(): mt.write("9")
            with mt.table_row():
                with mt.table_cell(): mt.write("70-79")
                with mt.table_cell(): mt.write("A")
                with mt.table_cell(): mt.write("8")
            with mt.table_row():
                with mt.table_cell(): mt.write("60-69")
                with mt.table_cell(): mt.write("B+")
                with mt.table_cell(): mt.write("7")
            with mt.table_row():
                with mt.table_cell(): mt.write("50-59")
                with mt.table_cell(): mt.write("B")
                with mt.table_cell(): mt.write("6")
            with mt.table_row():
                with mt.table_cell(): mt.write("40-49")
                with mt.table_cell(): mt.write("C")
                with mt.table_cell(): mt.write("5")

with mt.grid():
    with mt.row():
        with mt.col(6):
            previous_cgpa = mt.number_input(
                label="Previous CGPA",
                min_value=0.00,
                value=0.00,
                step=0.01,
            )
        with mt.col(6):
            previous_credit = mt.number_input(
                label="Previous Credit",
                min_value=0.0,
                value=0.0,
                step=0.5,
            )

number_of_subjects = mt.number_input(
    label="Number of Subjects",
    help="Enter the number of subjects you are taking this semester",
    min_value=1,
    max_value=10,
    value=5,
)

grade = [grades[0]] * number_of_subjects
credit = [0.0] * number_of_subjects
for i in range(number_of_subjects):
    mt.subheader(f"Subject #{i + 1}")
    with mt.grid():
        with mt.row():
            with mt.col(6):
                grade[i] = mt.selectbox(
                    label="Grade",
                    options=grades,
                    key=f"grade_{i}",
                    index=0,
                )
            with mt.col(6):
                credit[i] = mt.number_input(
                    label="Credit",
                    min_value=1.0,
                    max_value=10.0,
                    value=4.0,
                    step=0.5,
                    key=f"credit_{i}",
                )

if mt.button("Calculate"):
    grade_points = [grade_to_point[x] for x in grade]
    mt.info(f"Your semester GPA is {calculate_cgpa(grade_points, credit):.2f}")
    mt.success(
        f"Your Cumulative GPA is {calculate_cgpa(grade_points, credit, previous_cgpa, previous_credit):.2f}"
    )


mt.markdown("Made with ❤️ by [Kalpit B](https://dolphins.dev/)")