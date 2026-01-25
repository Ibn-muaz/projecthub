FACULTY_DEPARTMENTS = {
    "Faculty of Administration": [
        "Accounting", "Banking & Finance", "Business Administration", "Entrepreneurship", "Public Administration", "Taxation"
    ],
    "Faculty of Agriculture": [
        "Agricultural Economics and Extension", "Agronomy", "Animal Science", "Fisheries", "Forestry & Wildlife", "Home Science & Management"
    ],
    "Faculty of Arts": [
        "Arabic Studies", "English Language", "French", "Hausa", "History & Diplomatic Studies", "Islamic Studies", "Linguistics", "Philosophy", "Theatre & Cultural Studies"
    ],
    "Faculty of Education": [
        "Educational Management", "Guidance & Counselling", "Education and Biology", "Education and Chemistry", "Education and Physics", "Education and Economics", "Education and Geography"
    ],
    "Faculty of Engineering": [
        "Chemical/Processing Engineering", "Civil & Structural Engineering", "Electrical & Electronic Engineering"
    ],
    "Faculty of Environmental Science": [
        "Architecture", "Building Technology", "Environmental Management", "Estate Management"
    ],
    "Faculty of Law": [
        "Common and Islamic Law", "Private and Business Law", "Public and International Law"
    ],
    "Faculty of Medical and Health Sciences": [
        "Nursing Science", "MBBS (Medicine and Surgery)", "Medical Records", "Community Health"
    ],
    "Faculty of Natural and Applied Sciences": [
        "Biochemistry", "Chemistry", "Computer Science", "Data Science", "Cyber Security", "Geology & Mining", "Mathematics", "Microbiology", "Physics", "Plant Science & Biotechnology", "Statistics"
    ],
    "Faculty of Social Sciences": [
        "Criminology & Security Studies", "Economics", "Geography", "Mass Communication (Broadcasting, Journalism, Public Relations)", "Political Science", "Psychology", "Sociology"
    ]
}

# Flat list of departments (for validation and selects)
NSUK_DEPARTMENTS = sorted({dept for depts in FACULTY_DEPARTMENTS.values() for dept in depts})
