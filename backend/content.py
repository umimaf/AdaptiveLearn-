"""Sample learning content for the demo.

Each topic has three learning formats (text, audio, visual) and quiz
questions at two difficulty levels. Add subjects by appending to SUBJECTS.
Quiz tuples: (question type, difficulty, prompt, options, answer, explanation).
"""

SUBJECTS = [
    {
        "name": "Python Programming",
        "description": "Core Python skills, from variables to reusable functions and collections.",
        "topics": [
            {
                "key": "py_variables", "title": "Variables and Data Types", "difficulty_level": 1, "prerequisite": None,
                "simple_text": "A variable is a name that holds a value. Python works out the type of the value automatically.",
                "detailed_text": "Python has four basic types: int for whole numbers, float for decimals, str for text and bool for True or False. You create a variable with the assignment operator. Python is dynamically typed, so the same name can later hold a value of a different type.",
                "example_text": "A shopping total might be stored as price = 19.99 and item_count = 3, with the label name = 'notebook'.",
                "visual_text": "Diagram: a box labelled 'count' with an arrow to the value 42, and a box labelled 'name' with an arrow to the text 'Asha'.",
                "questions": [
                    ("mcq", 1, "Which statement stores the whole number 42 in a variable named count?",
                     ["count = 42", "count == 42", "42 = count", "count := '42'"], "count = 42",
                     "A single equals sign assigns a value to a name. == compares two values and stores nothing."),
                    ("true_false", 2, "In Python, a str value can be changed in place after it is created.",
                     ["True", "False"], "False",
                     "Strings are immutable. Methods such as replace() return a new string and leave the original unchanged."),
                ],
            },
            {
                "key": "py_control", "title": "Control Flow: Conditions and Loops", "difficulty_level": 1, "prerequisite": "py_variables",
                "simple_text": "Control flow decides which code runs and how many times. An if statement picks a path; a loop repeats one.",
                "detailed_text": "Use if, elif and else to branch on a condition. A for loop repeats over each item in a sequence such as a list or range(). A while loop repeats as long as its condition is True. Indentation defines which lines belong to a block.",
                "example_text": "A study app can print 'Pass' when a score is 50 or more, and ask five questions with for q in range(5).",
                "visual_text": "Flowchart: Start, then the test 'score >= 50?'. Yes leads to 'Print Pass'; No leads to 'Print Try again'; both lead to End.",
                "questions": [
                    ("mcq", 1, "What does range(3) produce when used in a for loop?",
                     ["0, 1, 2", "1, 2, 3", "0, 1, 2, 3", "3, 3, 3"], "0, 1, 2",
                     "range(n) starts at 0 and stops before n, so the values are 0, 1 and 2."),
                    ("mcq", 2, "Which loop suits a situation where you do not know in advance how many repetitions you need?",
                     ["for loop", "while loop", "if statement", "list comprehension"], "while loop",
                     "A while loop keeps going until its condition becomes False, so it fits unknown repetition counts."),
                ],
            },
            {
                "key": "py_functions", "title": "Functions and Reusable Code", "difficulty_level": 2, "prerequisite": "py_control",
                "simple_text": "A function is a named block of code you can call many times, often with inputs and a returned result.",
                "detailed_text": "Define a function with def, give it parameters for its inputs and send a result back with return. Functions reduce repetition and make code easier to test. Variables created inside a function are local and disappear when it ends.",
                "example_text": "def area(width, height): return width * height. Calling area(3, 4) returns 12, and the same function works for every room in a floor plan.",
                "visual_text": "Diagram: two inputs (width, height) enter a box labelled area(), and one output, 12, leaves it.",
                "questions": [
                    ("mcq", 2, "Which keyword sends a value back from a Python function?",
                     ["return", "give", "send", "output"], "return",
                     "return ends the function and passes the value back to the caller."),
                    ("mcq", 3, "Given def add(a, b): total = a + b, what does add(2, 3) return?",
                     ["5", "None", "2", "An error"], "None",
                     "There is no return statement, so the function returns None even though total is computed inside it."),
                ],
            },
            {
                "key": "py_collections", "title": "Lists and Dictionaries", "difficulty_level": 2, "prerequisite": "py_variables",
                "simple_text": "A list keeps an ordered collection of items. A dictionary stores values under keys so you can look them up by name.",
                "detailed_text": "Lists use square brackets and index from 0; you change them with append() and remove(). Dictionaries use curly braces with key: value pairs. Keys must be unique and immutable, and lookup by key is fast.",
                "example_text": "scores = {'maths': 78, 'python': 91} lets you read scores['python'], while grades = [70, 85, 92] lets you read grades[0] or average the list.",
                "visual_text": "Two panels: a list with index labels 0, 1, 2 above its values, and a dictionary whose keys 'maths' and 'python' point to their values.",
                "questions": [
                    ("mcq", 2, "What is the index of the first element in a Python list?",
                     ["0", "1", "-1", "It depends on the list"], "0",
                     "Python indexes sequences from zero, so the first item sits at index 0."),
                    ("mcq", 3, "What does scores.get('history') return if 'history' is not a key in scores?",
                     ["None", "0", "An error", "An empty string"], "None",
                     "get() returns None by default when a key is missing. scores['history'] would raise a KeyError instead."),
                ],
            },
        ],
    },
    {
        "name": "Database Management Systems",
        "description": "Relational databases, keys, SQL queries and normalization.",
        "topics": [
            {
                "key": "db_relational", "title": "The Relational Model and Keys", "difficulty_level": 1, "prerequisite": None,
                "simple_text": "A relational database stores data in tables of rows and columns. Keys link tables together.",
                "detailed_text": "Each table represents an entity, each row is one record and each column is an attribute. A primary key uniquely identifies a row. A foreign key refers to a primary key in another table, which keeps related data consistent.",
                "example_text": "In a school database, a Students table has student_id as its primary key, and an Enrolments table stores student_id as a foreign key.",
                "visual_text": "Two linked tables: Students (student_id PK, name) and Enrolments (enrol_id PK, student_id FK), joined by a line from the foreign key to the primary key.",
                "questions": [
                    ("mcq", 1, "What is the main purpose of a primary key?",
                     ["To uniquely identify each row", "To store the largest value in a table", "To speed up table deletion", "To link two databases"],
                     "To uniquely identify each row",
                     "A primary key guarantees that every row can be identified without ambiguity."),
                    ("true_false", 2, "A table can have more than one primary key.",
                     ["True", "False"], "False",
                     "A table has exactly one primary key, although that key may span several columns."),
                ],
            },
            {
                "key": "db_sql", "title": "SQL SELECT Queries", "difficulty_level": 2, "prerequisite": "db_relational",
                "simple_text": "SQL is the language for asking databases questions. SELECT chooses columns and FROM names the table.",
                "detailed_text": "A basic query is SELECT columns FROM table WHERE condition. WHERE filters rows, ORDER BY sorts results, and GROUP BY with aggregate functions such as COUNT and AVG summarises them.",
                "example_text": "SELECT name FROM students WHERE grade > 70 ORDER BY name; lists the names of students with a grade above 70, in alphabetical order.",
                "visual_text": "Pipeline: FROM the table, then WHERE filters rows, then SELECT picks columns, then ORDER BY sorts the output.",
                "questions": [
                    ("mcq", 2, "Which clause filters rows before they are returned?",
                     ["WHERE", "ORDER BY", "FROM", "LIMIT"], "WHERE",
                     "WHERE applies a condition to each row. ORDER BY only sorts, FROM names the table and LIMIT caps the row count."),
                    ("mcq", 3, "Which query counts the number of students in each grade?",
                     ["SELECT grade, COUNT(*) FROM students GROUP BY grade;",
                      "SELECT COUNT(grade) FROM students WHERE grade;",
                      "SELECT grade FROM students COUNT;",
                      "SELECT * GROUP grade COUNT;"],
                     "SELECT grade, COUNT(*) FROM students GROUP BY grade;",
                     "GROUP BY creates one group per grade, and COUNT(*) counts the rows in each group."),
                ],
            },
            {
                "key": "db_normalization", "title": "Normalization", "difficulty_level": 3, "prerequisite": "db_relational",
                "simple_text": "Normalization organises tables so each fact is stored once, which prevents update and deletion errors.",
                "detailed_text": "First normal form requires atomic values and no repeating groups. Second and third normal forms remove partial and transitive dependencies, so every non-key column depends only on the key. The trade-off is that some queries need more joins.",
                "example_text": "If a customer's address is repeated in every order row, changing it means updating many rows. Moving the address into a Customers table stores it once.",
                "visual_text": "Before and after: one wide table repeating the customer address, versus Customers and Orders tables linked by customer_id.",
                "questions": [
                    ("mcq", 3, "Which normal form requires each column to hold atomic, single values?",
                     ["First normal form (1NF)", "Second normal form (2NF)", "Third normal form (3NF)", "Fourth normal form (4NF)"],
                     "First normal form (1NF)",
                     "1NF requires atomic values and no repeating groups in each column."),
                    ("mcq", 3, "What is the main problem caused by storing a customer's address in every order row?",
                     ["Update anomalies", "Faster inserts", "Too many primary keys", "Automatic deletion of orders"],
                     "Update anomalies",
                     "Changing the address means updating many rows, and missing one leaves the data inconsistent."),
                ],
            },
        ],
    },
    {
        "name": "Data Structures and Algorithms",
        "description": "Explore how data is organized and how common algorithms process it.",
        "topics": [
            {
                "key": "dsa_arrays", "title": "Arrays and Indexing", "difficulty_level": 1, "prerequisite": None,
                "simple_text": "An array stores items in order. Each item has a numbered position called an index.",
                "detailed_text": "Arrays provide fast access when you know an item's index. In many programming languages, the first index is 0. Inserting or removing an item near the beginning can require shifting later items.",
                "example_text": "For scores = [72, 85, 91], scores[0] is 72 and scores[2] is 91.",
                "visual_text": "An indexed row of boxes shows 72 at index 0, 85 at index 1 and 91 at index 2.",
                "questions": [
                    ("mcq", 1, "What is the index of the first item in a zero-based array?",
                     ["0", "1", "-1", "The array length"], "0",
                     "Zero-based indexing starts at 0, so the first item is at index 0."),
                    ("mcq", 2, "What is a common advantage of accessing an array item by index?",
                     ["Fast direct access", "It always sorts the array", "It prevents duplicate values", "It uses no memory"],
                     "Fast direct access",
                     "An index lets a program go directly to a position without checking every earlier item."),
                ],
            },
            {
                "key": "dsa_stacks_queues", "title": "Stacks and Queues", "difficulty_level": 1, "prerequisite": "dsa_arrays",
                "simple_text": "A stack removes the newest item first. A queue removes the oldest item first.",
                "detailed_text": "A stack follows last-in, first-out (LIFO), like a pile of plates. A queue follows first-in, first-out (FIFO), like a line of people. Push and pop are common stack operations; enqueue and dequeue are common queue operations.",
                "example_text": "Undo history often behaves like a stack. A print queue handles documents in the order they were submitted.",
                "visual_text": "A stack shows the newest item on top; a queue shows the first item at the front and new items joining at the back.",
                "questions": [
                    ("mcq", 1, "Which item comes off a stack first?",
                     ["The most recently added item", "The oldest item", "The middle item", "A random item"],
                     "The most recently added item",
                     "Stacks are last-in, first-out: the most recently pushed item is popped first."),
                    ("mcq", 2, "Which structure is a natural fit for processing print jobs in arrival order?",
                     ["Queue", "Stack", "Tree", "Set"], "Queue",
                     "A queue is first-in, first-out, so jobs are handled in the order they arrive."),
                ],
            },
            {
                "key": "dsa_search_sort", "title": "Searching and Sorting", "difficulty_level": 2, "prerequisite": "dsa_arrays",
                "simple_text": "Searching finds an item; sorting puts items into a chosen order.",
                "detailed_text": "Linear search checks items one by one and works on unsorted data. Binary search repeatedly halves a sorted search range. Sorting algorithms arrange values, making some later searches and comparisons easier.",
                "example_text": "To find 8 in [2, 4, 6, 8, 10], a linear search checks in order. Binary search checks the middle value first and narrows the sorted range.",
                "visual_text": "A sorted number line is split in half repeatedly as binary search narrows down to the target.",
                "questions": [
                    ("mcq", 2, "What must be true before using binary search?",
                     ["The data is sorted", "The data has no numbers", "The target is the first item", "The array has even length"],
                     "The data is sorted",
                     "Binary search relies on sorted order to discard half of the remaining values each step."),
                    ("mcq", 3, "How does binary search shrink the search range after each comparison?",
                     ["It removes about half the range", "It checks every item again", "It reverses the array", "It adds a new item"],
                     "It removes about half the range",
                     "Each comparison tells binary search which half cannot contain the target."),
                ],
            },
        ],
    },
]


def seed_content(conn):
    """Add missing sample lessons without replacing existing learner data."""
    import json

    topic_ids = {}
    pending_prereqs = []
    for subject in SUBJECTS:
        existing_subject = conn.execute(
            "SELECT id FROM subjects WHERE name = ?", (subject["name"],)
        ).fetchone()
        if existing_subject:
            sid = existing_subject[0]
        else:
            sid = conn.execute(
                "INSERT INTO subjects (name, description) VALUES (?, ?)",
                (subject["name"], subject["description"]),
            ).lastrowid
        for order, t in enumerate(subject["topics"], start=1):
            existing_topic = conn.execute(
                "SELECT id FROM topics WHERE subject_id = ? AND title = ?", (sid, t["title"])
            ).fetchone()
            if existing_topic:
                tid = existing_topic[0]
            else:
                tid = conn.execute(
                    """INSERT INTO topics (subject_id, title, difficulty_level, order_index,
                       simple_text, detailed_text, example_text, visual_text)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (sid, t["title"], t["difficulty_level"], order, t["simple_text"],
                     t["detailed_text"], t["example_text"], t["visual_text"]),
                ).lastrowid
                for qtype, diff, prompt, options, answer, explanation in t["questions"]:
                    conn.execute(
                        """INSERT INTO quiz_questions (topic_id, qtype, difficulty, prompt, options, answer, explanation)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (tid, qtype, diff, prompt, json.dumps(options), answer, explanation),
                    )
            topic_ids[t["key"]] = tid
            if t["prerequisite"]:
                pending_prereqs.append((t["prerequisite"], tid))

    for prereq_key, tid in pending_prereqs:
        conn.execute("UPDATE topics SET prerequisite_id = ? WHERE id = ?", (topic_ids[prereq_key], tid))
