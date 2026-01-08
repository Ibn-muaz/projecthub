FACULTY_DEPARTMENTS = {
    "Faculty of Administration": [
        "Accounting",
        "Entrepreneurship Studies",
        "Public Administration",
        "Business Administration",
        "Banking and Finance",
    ],
    "Faculty of Arts": [
        "English Language",
        "Arabic Studies",
        "French",
        "History",
        "Christian Religious Studies",
        "Islamic Studies",
        "Theatre and Cultural Studies",
    ],
    "Faculty of Education": [
        "Education and Biology",
        "Education and Chemistry",
        "Education and Christian Religious Studies",
        "Education and Economics",
        "Education and English Language",
        "Education and French",
        "Education and Geography",
        "Education and History",
        "Education and Integrated Science",
        "Education and Islamic Studies",
        "Education and Mathematics",
        "Education and Physics",
    ],
    "Faculty of Environmental Science": [
        "Environmental Management",
        "Architecture",
        "Geography",
        "Urban and Regional Planning",
    ],
    "Faculty of Law": [
        "Law",
    ],
    "Faculty of Natural and Applied Sciences": [
        "Chemistry",
        "Computer Science",
        "Geology and Mining",
        "Mathematics",
        "Microbiology",
        "Physics",
        "Biochemistry",
        "Statistics",
        "Plant Science and Biotechnology",
    ],
    "Faculty of Social Sciences": [
        "Economics",
        "Psychology",
        "Mass Communication",
        "Political Science",
        "Sociology",
    ],
    "Faculty of Medical and Health Sciences": [
        "Nursing",
    ],
    "Faculty of Agriculture": [
        "Agricultural Economics and Extension",
        "Agronomy",
        "Animal Science",
        "Forestry, Wildlife and Ecotourism",
        "Home Science and Management",
    ],
}

# Flat list of departments (for validation and selects)
NSUK_DEPARTMENTS = sorted({dept for depts in FACULTY_DEPARTMENTS.values() for dept in depts})
