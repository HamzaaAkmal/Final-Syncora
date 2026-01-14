"""
Pakistan Curriculum Data
========================

Contains structured curriculum data for:
- Mathematics (Grades 6-10)
- Science (Grades 6-10)
- English (Grades 6-10)
- Urdu (Grades 6-10)
- Pakistan Studies (Grades 9-10)

Based on:
- Punjab Curriculum and Textbook Board (PCTB)
- National Curriculum of Pakistan
- Sindh Curriculum
"""

from .models import (
    Subject,
    Chapter,
    Topic,
    LearningObjective,
    CurriculumBoard,
    DifficultyLevel,
)

# ============================================================================
# MATHEMATICS CURRICULUM
# ============================================================================

MATH_GRADE_9_TOPICS = [
    # Chapter 1: Matrices and Determinants
    Topic(
        id="math_9_1_1",
        name="Introduction to Matrices",
        name_ur="میٹرکس کا تعارف",
        chapter_id="math_9_ch1",
        subject_id="mathematics",
        grade=9,
        order=1,
        description="Understanding matrices, types, and basic operations",
        description_ur="میٹرکس، اقسام، اور بنیادی عملیات کو سمجھنا",
        objectives=[
            LearningObjective(
                id="math_9_1_1_obj1",
                description="Define a matrix and identify its elements",
                description_ur="میٹرکس کی تعریف اور اس کے عناصر کی شناخت",
                bloom_level="remember",
                keywords=["matrix", "elements", "rows", "columns"],
            ),
            LearningObjective(
                id="math_9_1_1_obj2",
                description="Classify matrices by type (row, column, square, null)",
                description_ur="قسم کے لحاظ سے میٹرکس کی درجہ بندی",
                bloom_level="understand",
                keywords=["row matrix", "column matrix", "square matrix"],
            ),
        ],
        prerequisites=[],
        estimated_hours=2,
        difficulty=DifficultyLevel.MEDIUM,
        keywords=["matrix", "matrices", "array", "میٹرکس"],
    ),
    Topic(
        id="math_9_1_2",
        name="Matrix Operations",
        name_ur="میٹرکس کی عملیات",
        chapter_id="math_9_ch1",
        subject_id="mathematics",
        grade=9,
        order=2,
        description="Addition, subtraction, and multiplication of matrices",
        description_ur="میٹرکس کی جمع، تفریق، اور ضرب",
        objectives=[
            LearningObjective(
                id="math_9_1_2_obj1",
                description="Add and subtract matrices",
                description_ur="میٹرکس کو جمع اور تفریق کرنا",
                bloom_level="apply",
                keywords=["addition", "subtraction", "matrix operations"],
            ),
            LearningObjective(
                id="math_9_1_2_obj2",
                description="Multiply matrices and scalars",
                description_ur="میٹرکس اور اسکیلر کو ضرب کرنا",
                bloom_level="apply",
                keywords=["multiplication", "scalar", "matrix product"],
            ),
        ],
        prerequisites=["math_9_1_1"],
        estimated_hours=3,
        difficulty=DifficultyLevel.MEDIUM,
        keywords=["matrix addition", "matrix multiplication", "میٹرکس عملیات"],
    ),
    Topic(
        id="math_9_1_3",
        name="Determinants",
        name_ur="ڈیٹرمیننٹس",
        chapter_id="math_9_ch1",
        subject_id="mathematics",
        grade=9,
        order=3,
        description="Calculating determinants of 2x2 and 3x3 matrices",
        description_ur="2x2 اور 3x3 میٹرکس کے ڈیٹرمیننٹس کا حساب",
        objectives=[
            LearningObjective(
                id="math_9_1_3_obj1",
                description="Calculate determinant of a 2x2 matrix",
                description_ur="2x2 میٹرکس کا ڈیٹرمیننٹ نکالنا",
                bloom_level="apply",
                keywords=["determinant", "2x2", "calculation"],
            ),
        ],
        prerequisites=["math_9_1_1", "math_9_1_2"],
        estimated_hours=2,
        difficulty=DifficultyLevel.HARD,
        keywords=["determinant", "ڈیٹرمیننٹ", "matrix inverse"],
    ),
    # Chapter 2: Real and Complex Numbers
    Topic(
        id="math_9_2_1",
        name="Real Numbers",
        name_ur="حقیقی اعداد",
        chapter_id="math_9_ch2",
        subject_id="mathematics",
        grade=9,
        order=1,
        description="Properties and operations on real numbers",
        description_ur="حقیقی اعداد کی خصوصیات اور عملیات",
        objectives=[
            LearningObjective(
                id="math_9_2_1_obj1",
                description="Identify and classify real numbers",
                description_ur="حقیقی اعداد کی شناخت اور درجہ بندی",
                bloom_level="understand",
                keywords=["real numbers", "rational", "irrational"],
            ),
        ],
        prerequisites=[],
        estimated_hours=2,
        difficulty=DifficultyLevel.EASY,
        keywords=["real numbers", "حقیقی اعداد", "number system"],
    ),
    Topic(
        id="math_9_2_2",
        name="Complex Numbers",
        name_ur="مختلط اعداد",
        chapter_id="math_9_ch2",
        subject_id="mathematics",
        grade=9,
        order=2,
        description="Introduction to complex numbers and operations",
        description_ur="مختلط اعداد کا تعارف اور عملیات",
        objectives=[
            LearningObjective(
                id="math_9_2_2_obj1",
                description="Define complex numbers and imaginary unit",
                description_ur="مختلط اعداد اور فرضی یونٹ کی تعریف",
                bloom_level="remember",
                keywords=["complex", "imaginary", "i"],
            ),
            LearningObjective(
                id="math_9_2_2_obj2",
                description="Perform operations on complex numbers",
                description_ur="مختلط اعداد پر عملیات کرنا",
                bloom_level="apply",
                keywords=["addition", "subtraction", "multiplication", "complex"],
            ),
        ],
        prerequisites=["math_9_2_1"],
        estimated_hours=3,
        difficulty=DifficultyLevel.MEDIUM,
        keywords=["complex numbers", "مختلط اعداد", "imaginary"],
    ),
    # Chapter 3: Logarithms
    Topic(
        id="math_9_3_1",
        name="Introduction to Logarithms",
        name_ur="لوگارتھم کا تعارف",
        chapter_id="math_9_ch3",
        subject_id="mathematics",
        grade=9,
        order=1,
        description="Understanding logarithms and their relationship with exponents",
        description_ur="لوگارتھم اور ایکسپوننٹس کے ساتھ ان کا تعلق",
        objectives=[
            LearningObjective(
                id="math_9_3_1_obj1",
                description="Define logarithm and convert between exponential and logarithmic forms",
                description_ur="لوگارتھم کی تعریف اور ایکسپوننشل اور لوگارتھمک فارمز کے درمیان تبدیلی",
                bloom_level="understand",
                keywords=["logarithm", "exponent", "base"],
            ),
        ],
        prerequisites=["math_9_2_1"],
        estimated_hours=2,
        difficulty=DifficultyLevel.MEDIUM,
        keywords=["logarithm", "لوگارتھم", "log", "exponent"],
    ),
    Topic(
        id="math_9_3_2",
        name="Laws of Logarithms",
        name_ur="لوگارتھم کے قوانین",
        chapter_id="math_9_ch3",
        subject_id="mathematics",
        grade=9,
        order=2,
        description="Product, quotient, and power rules of logarithms",
        description_ur="لوگارتھم کے ضرب، تقسیم، اور طاقت کے قوانین",
        objectives=[
            LearningObjective(
                id="math_9_3_2_obj1",
                description="Apply laws of logarithms to simplify expressions",
                description_ur="اظہارات کو آسان بنانے کے لیے لوگارتھم کے قوانین کا اطلاق",
                bloom_level="apply",
                keywords=["product rule", "quotient rule", "power rule"],
            ),
        ],
        prerequisites=["math_9_3_1"],
        estimated_hours=3,
        difficulty=DifficultyLevel.HARD,
        keywords=["log rules", "لوگارتھم قوانین", "logarithm laws"],
    ),
    # Chapter 4: Algebraic Expressions
    Topic(
        id="math_9_4_1",
        name="Algebraic Expressions and Identities",
        name_ur="الجبری اظہارات اور شناختیں",
        chapter_id="math_9_ch4",
        subject_id="mathematics",
        grade=9,
        order=1,
        description="Simplifying algebraic expressions using identities",
        description_ur="شناختوں کا استعمال کرتے ہوئے الجبری اظہارات کو آسان بنانا",
        objectives=[
            LearningObjective(
                id="math_9_4_1_obj1",
                description="Apply algebraic identities to simplify expressions",
                description_ur="اظہارات کو آسان بنانے کے لیے الجبری شناختوں کا اطلاق",
                bloom_level="apply",
                keywords=["identity", "algebraic", "simplify"],
            ),
        ],
        prerequisites=[],
        estimated_hours=2,
        difficulty=DifficultyLevel.MEDIUM,
        keywords=["algebra", "الجبر", "identities", "expressions"],
    ),
    Topic(
        id="math_9_4_2",
        name="Factorization",
        name_ur="تجزیہ",
        chapter_id="math_9_ch4",
        subject_id="mathematics",
        grade=9,
        order=2,
        description="Factoring algebraic expressions",
        description_ur="الجبری اظہارات کا تجزیہ",
        objectives=[
            LearningObjective(
                id="math_9_4_2_obj1",
                description="Factor quadratic expressions",
                description_ur="مربع اظہارات کا تجزیہ",
                bloom_level="apply",
                keywords=["factor", "quadratic", "polynomial"],
            ),
        ],
        prerequisites=["math_9_4_1"],
        estimated_hours=3,
        difficulty=DifficultyLevel.MEDIUM,
        keywords=["factorization", "تجزیہ", "factors", "polynomial"],
    ),
    # Chapter 5: Linear Equations and Inequalities
    Topic(
        id="math_9_5_1",
        name="Linear Equations in One Variable",
        name_ur="ایک متغیر میں لکیری مساوات",
        chapter_id="math_9_ch5",
        subject_id="mathematics",
        grade=9,
        order=1,
        description="Solving linear equations with one variable",
        description_ur="ایک متغیر کے ساتھ لکیری مساوات کو حل کرنا",
        objectives=[
            LearningObjective(
                id="math_9_5_1_obj1",
                description="Solve linear equations in one variable",
                description_ur="ایک متغیر میں لکیری مساوات حل کرنا",
                bloom_level="apply",
                keywords=["linear", "equation", "variable", "solve"],
            ),
        ],
        prerequisites=["math_9_4_1"],
        estimated_hours=2,
        difficulty=DifficultyLevel.EASY,
        keywords=["linear equation", "لکیری مساوات", "solve", "variable"],
    ),
    Topic(
        id="math_9_5_2",
        name="Linear Equations in Two Variables",
        name_ur="دو متغیرات میں لکیری مساوات",
        chapter_id="math_9_ch5",
        subject_id="mathematics",
        grade=9,
        order=2,
        description="Solving systems of linear equations",
        description_ur="لکیری مساوات کے نظام کو حل کرنا",
        objectives=[
            LearningObjective(
                id="math_9_5_2_obj1",
                description="Solve systems of linear equations using substitution and elimination",
                description_ur="متبادل اور خاتمے کا استعمال کرتے ہوئے لکیری مساوات کے نظام کو حل کرنا",
                bloom_level="apply",
                keywords=["system", "substitution", "elimination", "simultaneous"],
            ),
        ],
        prerequisites=["math_9_5_1"],
        estimated_hours=4,
        difficulty=DifficultyLevel.MEDIUM,
        keywords=["simultaneous equations", "ہم وقت مساوات", "system", "two variables"],
    ),
    Topic(
        id="math_9_5_3",
        name="Linear Inequalities",
        name_ur="لکیری عدم مساوات",
        chapter_id="math_9_ch5",
        subject_id="mathematics",
        grade=9,
        order=3,
        description="Solving and graphing linear inequalities",
        description_ur="لکیری عدم مساوات کو حل کرنا اور گراف بنانا",
        objectives=[
            LearningObjective(
                id="math_9_5_3_obj1",
                description="Solve and graph linear inequalities",
                description_ur="لکیری عدم مساوات کو حل اور گراف کرنا",
                bloom_level="apply",
                keywords=["inequality", "graph", "solution set"],
            ),
        ],
        prerequisites=["math_9_5_1"],
        estimated_hours=3,
        difficulty=DifficultyLevel.MEDIUM,
        keywords=["inequality", "عدم مساوات", "less than", "greater than"],
    ),
    # Chapter 6: Quadratic Equations
    Topic(
        id="math_9_6_1",
        name="Quadratic Equations",
        name_ur="مربع مساوات",
        chapter_id="math_9_ch6",
        subject_id="mathematics",
        grade=9,
        order=1,
        description="Solving quadratic equations by factorization and formula",
        description_ur="تجزیہ اور فارمولے کے ذریعے مربع مساوات کو حل کرنا",
        objectives=[
            LearningObjective(
                id="math_9_6_1_obj1",
                description="Solve quadratic equations using factorization",
                description_ur="تجزیہ کا استعمال کرتے ہوئے مربع مساوات حل کرنا",
                bloom_level="apply",
                keywords=["quadratic", "factorization", "roots"],
            ),
            LearningObjective(
                id="math_9_6_1_obj2",
                description="Apply quadratic formula to solve equations",
                description_ur="مساوات حل کرنے کے لیے مربع فارمولے کا اطلاق",
                bloom_level="apply",
                keywords=["quadratic formula", "discriminant", "roots"],
            ),
        ],
        prerequisites=["math_9_4_2", "math_9_5_1"],
        estimated_hours=4,
        difficulty=DifficultyLevel.HARD,
        keywords=["quadratic", "مربع مساوات", "ax²+bx+c", "roots"],
    ),
]

MATH_GRADE_9_CHAPTERS = [
    Chapter(
        id="math_9_ch1",
        name="Matrices and Determinants",
        name_ur="میٹرکس اور ڈیٹرمیننٹس",
        subject_id="mathematics",
        grade=9,
        order=1,
        description="Study of matrices, their operations, and determinants",
        description_ur="میٹرکس، ان کی عملیات، اور ڈیٹرمیننٹس کا مطالعہ",
        topics=[t for t in MATH_GRADE_9_TOPICS if t.chapter_id == "math_9_ch1"],
    ),
    Chapter(
        id="math_9_ch2",
        name="Real and Complex Numbers",
        name_ur="حقیقی اور مختلط اعداد",
        subject_id="mathematics",
        grade=9,
        order=2,
        description="Number systems including real and complex numbers",
        description_ur="نمبر سسٹم جس میں حقیقی اور مختلط اعداد شامل ہیں",
        topics=[t for t in MATH_GRADE_9_TOPICS if t.chapter_id == "math_9_ch2"],
    ),
    Chapter(
        id="math_9_ch3",
        name="Logarithms",
        name_ur="لوگارتھم",
        subject_id="mathematics",
        grade=9,
        order=3,
        description="Logarithms and their applications",
        description_ur="لوگارتھم اور ان کے استعمال",
        topics=[t for t in MATH_GRADE_9_TOPICS if t.chapter_id == "math_9_ch3"],
    ),
    Chapter(
        id="math_9_ch4",
        name="Algebraic Expressions and Algebraic Formulas",
        name_ur="الجبری اظہارات اور الجبری فارمولے",
        subject_id="mathematics",
        grade=9,
        order=4,
        description="Working with algebraic expressions and identities",
        description_ur="الجبری اظہارات اور شناختوں کے ساتھ کام کرنا",
        topics=[t for t in MATH_GRADE_9_TOPICS if t.chapter_id == "math_9_ch4"],
    ),
    Chapter(
        id="math_9_ch5",
        name="Linear Equations and Inequalities",
        name_ur="لکیری مساوات اور عدم مساوات",
        subject_id="mathematics",
        grade=9,
        order=5,
        description="Solving linear equations and inequalities",
        description_ur="لکیری مساوات اور عدم مساوات کو حل کرنا",
        topics=[t for t in MATH_GRADE_9_TOPICS if t.chapter_id == "math_9_ch5"],
    ),
    Chapter(
        id="math_9_ch6",
        name="Quadratic Equations",
        name_ur="مربع مساوات",
        subject_id="mathematics",
        grade=9,
        order=6,
        description="Solving quadratic equations",
        description_ur="مربع مساوات کو حل کرنا",
        topics=[t for t in MATH_GRADE_9_TOPICS if t.chapter_id == "math_9_ch6"],
    ),
]

# ============================================================================
# SCIENCE CURRICULUM (General Science Grade 9)
# ============================================================================

SCIENCE_GRADE_9_TOPICS = [
    # Chapter 1: Introduction to Biology
    Topic(
        id="sci_9_1_1",
        name="Introduction to Biology",
        name_ur="حیاتیات کا تعارف",
        chapter_id="sci_9_ch1",
        subject_id="science",
        grade=9,
        order=1,
        description="What is biology and its branches",
        description_ur="حیاتیات کیا ہے اور اس کی شاخیں",
        objectives=[
            LearningObjective(
                id="sci_9_1_1_obj1",
                description="Define biology and list its major branches",
                description_ur="حیاتیات کی تعریف اور اس کی اہم شاخوں کی فہرست",
                bloom_level="remember",
                keywords=["biology", "botany", "zoology", "microbiology"],
            ),
        ],
        prerequisites=[],
        estimated_hours=1,
        difficulty=DifficultyLevel.EASY,
        keywords=["biology", "حیاتیات", "life science"],
    ),
    Topic(
        id="sci_9_1_2",
        name="Cell Structure and Function",
        name_ur="خلیے کی ساخت اور کام",
        chapter_id="sci_9_ch1",
        subject_id="science",
        grade=9,
        order=2,
        description="Understanding the structure and function of cells",
        description_ur="خلیوں کی ساخت اور کام کو سمجھنا",
        objectives=[
            LearningObjective(
                id="sci_9_1_2_obj1",
                description="Identify parts of a cell and their functions",
                description_ur="خلیے کے حصوں اور ان کے کاموں کی شناخت",
                bloom_level="understand",
                keywords=["cell", "nucleus", "cytoplasm", "membrane"],
            ),
        ],
        prerequisites=["sci_9_1_1"],
        estimated_hours=2,
        difficulty=DifficultyLevel.MEDIUM,
        keywords=["cell", "خلیہ", "organelle", "nucleus"],
    ),
    # Chapter 2: Matter and Its States
    Topic(
        id="sci_9_2_1",
        name="States of Matter",
        name_ur="مادے کی حالتیں",
        chapter_id="sci_9_ch2",
        subject_id="science",
        grade=9,
        order=1,
        description="Solid, liquid, gas and their properties",
        description_ur="ٹھوس، مائع، گیس اور ان کی خصوصیات",
        objectives=[
            LearningObjective(
                id="sci_9_2_1_obj1",
                description="Describe properties of solids, liquids, and gases",
                description_ur="ٹھوس، مائع، اور گیسوں کی خصوصیات بیان کریں",
                bloom_level="understand",
                keywords=["solid", "liquid", "gas", "matter"],
            ),
        ],
        prerequisites=[],
        estimated_hours=2,
        difficulty=DifficultyLevel.EASY,
        keywords=["matter", "مادہ", "states", "solid", "liquid", "gas"],
    ),
    Topic(
        id="sci_9_2_2",
        name="Atomic Structure",
        name_ur="ایٹم کی ساخت",
        chapter_id="sci_9_ch2",
        subject_id="science",
        grade=9,
        order=2,
        description="Structure of atoms and subatomic particles",
        description_ur="ایٹموں کی ساخت اور ذیلی ایٹمی ذرات",
        objectives=[
            LearningObjective(
                id="sci_9_2_2_obj1",
                description="Identify protons, neutrons, and electrons",
                description_ur="پروٹون، نیوٹرون، اور الیکٹرون کی شناخت",
                bloom_level="remember",
                keywords=["atom", "proton", "neutron", "electron"],
            ),
        ],
        prerequisites=["sci_9_2_1"],
        estimated_hours=2,
        difficulty=DifficultyLevel.MEDIUM,
        keywords=["atom", "ایٹم", "atomic", "subatomic"],
    ),
    # Chapter 3: Motion and Force
    Topic(
        id="sci_9_3_1",
        name="Motion and Speed",
        name_ur="حرکت اور رفتار",
        chapter_id="sci_9_ch3",
        subject_id="science",
        grade=9,
        order=1,
        description="Understanding motion, speed, and velocity",
        description_ur="حرکت، رفتار، اور ویلاسٹی کو سمجھنا",
        objectives=[
            LearningObjective(
                id="sci_9_3_1_obj1",
                description="Calculate speed and velocity",
                description_ur="رفتار اور ویلاسٹی کا حساب",
                bloom_level="apply",
                keywords=["speed", "velocity", "distance", "time"],
            ),
        ],
        prerequisites=[],
        estimated_hours=2,
        difficulty=DifficultyLevel.MEDIUM,
        keywords=["motion", "حرکت", "speed", "رفتار", "velocity"],
    ),
    Topic(
        id="sci_9_3_2",
        name="Newton's Laws of Motion",
        name_ur="نیوٹن کے حرکت کے قوانین",
        chapter_id="sci_9_ch3",
        subject_id="science",
        grade=9,
        order=2,
        description="Understanding Newton's three laws of motion",
        description_ur="نیوٹن کے حرکت کے تین قوانین کو سمجھنا",
        objectives=[
            LearningObjective(
                id="sci_9_3_2_obj1",
                description="State and apply Newton's laws of motion",
                description_ur="نیوٹن کے حرکت کے قوانین بیان اور لاگو کریں",
                bloom_level="apply",
                keywords=["Newton", "force", "acceleration", "inertia"],
            ),
        ],
        prerequisites=["sci_9_3_1"],
        estimated_hours=3,
        difficulty=DifficultyLevel.HARD,
        keywords=["Newton", "force", "قوت", "laws", "motion"],
    ),
]

SCIENCE_GRADE_9_CHAPTERS = [
    Chapter(
        id="sci_9_ch1",
        name="Introduction to Biology",
        name_ur="حیاتیات کا تعارف",
        subject_id="science",
        grade=9,
        order=1,
        description="Basic concepts of biology and cell structure",
        description_ur="حیاتیات اور خلیے کی ساخت کے بنیادی تصورات",
        topics=[t for t in SCIENCE_GRADE_9_TOPICS if t.chapter_id == "sci_9_ch1"],
    ),
    Chapter(
        id="sci_9_ch2",
        name="Matter and Atomic Structure",
        name_ur="مادہ اور ایٹم کی ساخت",
        subject_id="science",
        grade=9,
        order=2,
        description="Properties of matter and atomic structure",
        description_ur="مادے کی خصوصیات اور ایٹم کی ساخت",
        topics=[t for t in SCIENCE_GRADE_9_TOPICS if t.chapter_id == "sci_9_ch2"],
    ),
    Chapter(
        id="sci_9_ch3",
        name="Motion and Force",
        name_ur="حرکت اور قوت",
        subject_id="science",
        grade=9,
        order=3,
        description="Understanding motion and forces",
        description_ur="حرکت اور قوتوں کو سمجھنا",
        topics=[t for t in SCIENCE_GRADE_9_TOPICS if t.chapter_id == "sci_9_ch3"],
    ),
]

# ============================================================================
# ENGLISH CURRICULUM
# ============================================================================

ENGLISH_GRADE_9_TOPICS = [
    Topic(
        id="eng_9_1_1",
        name="Parts of Speech",
        name_ur="اجزائے کلام",
        chapter_id="eng_9_ch1",
        subject_id="english",
        grade=9,
        order=1,
        description="Understanding nouns, verbs, adjectives, and other parts of speech",
        description_ur="اسم، فعل، صفت، اور دیگر اجزائے کلام کو سمجھنا",
        objectives=[
            LearningObjective(
                id="eng_9_1_1_obj1",
                description="Identify and use different parts of speech",
                description_ur="مختلف اجزائے کلام کی شناخت اور استعمال",
                bloom_level="apply",
                keywords=["noun", "verb", "adjective", "adverb"],
            ),
        ],
        prerequisites=[],
        estimated_hours=2,
        difficulty=DifficultyLevel.EASY,
        keywords=["grammar", "parts of speech", "گرامر"],
    ),
    Topic(
        id="eng_9_1_2",
        name="Tenses",
        name_ur="زمانے",
        chapter_id="eng_9_ch1",
        subject_id="english",
        grade=9,
        order=2,
        description="Past, present, and future tenses",
        description_ur="ماضی، حال، اور مستقبل کے زمانے",
        objectives=[
            LearningObjective(
                id="eng_9_1_2_obj1",
                description="Use correct tense forms in sentences",
                description_ur="جملوں میں صحیح زمانے کی شکلیں استعمال کریں",
                bloom_level="apply",
                keywords=["past", "present", "future", "tense"],
            ),
        ],
        prerequisites=["eng_9_1_1"],
        estimated_hours=3,
        difficulty=DifficultyLevel.MEDIUM,
        keywords=["tenses", "زمانے", "past", "present", "future"],
    ),
    Topic(
        id="eng_9_2_1",
        name="Reading Comprehension",
        name_ur="مطالعہ فہم",
        chapter_id="eng_9_ch2",
        subject_id="english",
        grade=9,
        order=1,
        description="Understanding and analyzing texts",
        description_ur="متن کو سمجھنا اور تجزیہ کرنا",
        objectives=[
            LearningObjective(
                id="eng_9_2_1_obj1",
                description="Analyze texts and answer comprehension questions",
                description_ur="متن کا تجزیہ کریں اور فہم کے سوالات کے جوابات دیں",
                bloom_level="analyze",
                keywords=["reading", "comprehension", "analysis"],
            ),
        ],
        prerequisites=[],
        estimated_hours=3,
        difficulty=DifficultyLevel.MEDIUM,
        keywords=["reading", "مطالعہ", "comprehension", "فہم"],
    ),
    Topic(
        id="eng_9_2_2",
        name="Essay Writing",
        name_ur="مضمون نگاری",
        chapter_id="eng_9_ch2",
        subject_id="english",
        grade=9,
        order=2,
        description="Writing structured essays",
        description_ur="منظم مضامین لکھنا",
        objectives=[
            LearningObjective(
                id="eng_9_2_2_obj1",
                description="Write well-structured essays with introduction, body, and conclusion",
                description_ur="تعارف، جسم، اور نتیجے کے ساتھ اچھی طرح سے منظم مضامین لکھیں",
                bloom_level="create",
                keywords=["essay", "writing", "structure"],
            ),
        ],
        prerequisites=["eng_9_1_2"],
        estimated_hours=4,
        difficulty=DifficultyLevel.HARD,
        keywords=["essay", "مضمون", "writing", "تحریر"],
    ),
]

ENGLISH_GRADE_9_CHAPTERS = [
    Chapter(
        id="eng_9_ch1",
        name="Grammar Fundamentals",
        name_ur="گرامر کے بنیادی اصول",
        subject_id="english",
        grade=9,
        order=1,
        description="Essential grammar concepts",
        description_ur="ضروری گرامر کے تصورات",
        topics=[t for t in ENGLISH_GRADE_9_TOPICS if t.chapter_id == "eng_9_ch1"],
    ),
    Chapter(
        id="eng_9_ch2",
        name="Reading and Writing Skills",
        name_ur="پڑھنے اور لکھنے کی مہارتیں",
        subject_id="english",
        grade=9,
        order=2,
        description="Developing reading and writing abilities",
        description_ur="پڑھنے اور لکھنے کی صلاحیتوں کی ترقی",
        topics=[t for t in ENGLISH_GRADE_9_TOPICS if t.chapter_id == "eng_9_ch2"],
    ),
]

# ============================================================================
# URDU CURRICULUM
# ============================================================================

URDU_GRADE_9_TOPICS = [
    Topic(
        id="urdu_9_1_1",
        name="اردو نثر - کہانی",
        name_ur="اردو نثر - کہانی",
        chapter_id="urdu_9_ch1",
        subject_id="urdu",
        grade=9,
        order=1,
        description="Urdu prose and story writing",
        description_ur="اردو نثر اور کہانی لکھنا",
        objectives=[
            LearningObjective(
                id="urdu_9_1_1_obj1",
                description="Read and understand Urdu prose",
                description_ur="اردو نثر پڑھیں اور سمجھیں",
                bloom_level="understand",
                keywords=["prose", "نثر", "story", "کہانی"],
            ),
        ],
        prerequisites=[],
        estimated_hours=2,
        difficulty=DifficultyLevel.MEDIUM,
        keywords=["نثر", "prose", "کہانی", "story"],
    ),
    Topic(
        id="urdu_9_1_2",
        name="اردو شاعری",
        name_ur="اردو شاعری",
        chapter_id="urdu_9_ch1",
        subject_id="urdu",
        grade=9,
        order=2,
        description="Understanding and appreciating Urdu poetry",
        description_ur="اردو شاعری کو سمجھنا اور سراہنا",
        objectives=[
            LearningObjective(
                id="urdu_9_1_2_obj1",
                description="Analyze and appreciate Urdu poetry",
                description_ur="اردو شاعری کا تجزیہ اور تعریف کریں",
                bloom_level="analyze",
                keywords=["poetry", "شاعری", "ghazal", "غزل"],
            ),
        ],
        prerequisites=["urdu_9_1_1"],
        estimated_hours=3,
        difficulty=DifficultyLevel.HARD,
        keywords=["شاعری", "poetry", "غزل", "نظم"],
    ),
    Topic(
        id="urdu_9_2_1",
        name="اردو گرامر",
        name_ur="اردو گرامر",
        chapter_id="urdu_9_ch2",
        subject_id="urdu",
        grade=9,
        order=1,
        description="Urdu grammar rules and usage",
        description_ur="اردو گرامر کے قوانین اور استعمال",
        objectives=[
            LearningObjective(
                id="urdu_9_2_1_obj1",
                description="Apply Urdu grammar rules correctly",
                description_ur="اردو گرامر کے قوانین کا صحیح اطلاق",
                bloom_level="apply",
                keywords=["grammar", "گرامر", "rules", "قواعد"],
            ),
        ],
        prerequisites=[],
        estimated_hours=3,
        difficulty=DifficultyLevel.MEDIUM,
        keywords=["گرامر", "grammar", "قواعد", "rules"],
    ),
]

URDU_GRADE_9_CHAPTERS = [
    Chapter(
        id="urdu_9_ch1",
        name="اردو ادب",
        name_ur="اردو ادب",
        subject_id="urdu",
        grade=9,
        order=1,
        description="Urdu literature - prose and poetry",
        description_ur="اردو ادب - نثر اور شاعری",
        topics=[t for t in URDU_GRADE_9_TOPICS if t.chapter_id == "urdu_9_ch1"],
    ),
    Chapter(
        id="urdu_9_ch2",
        name="قواعد اور تحریر",
        name_ur="قواعد اور تحریر",
        subject_id="urdu",
        grade=9,
        order=2,
        description="Grammar and writing skills",
        description_ur="گرامر اور تحریری مہارتیں",
        topics=[t for t in URDU_GRADE_9_TOPICS if t.chapter_id == "urdu_9_ch2"],
    ),
]

# ============================================================================
# SUBJECTS DEFINITION
# ============================================================================

SUBJECTS = [
    Subject(
        id="mathematics",
        name="Mathematics",
        name_ur="ریاضی",
        board=CurriculumBoard.PUNJAB,
        grades=[6, 7, 8, 9, 10, 11, 12],
        description="Study of numbers, quantities, and shapes",
        description_ur="اعداد، مقداروں، اور شکلوں کا مطالعہ",
        icon="📐",
        chapters={9: MATH_GRADE_9_CHAPTERS},
    ),
    Subject(
        id="science",
        name="General Science",
        name_ur="عام سائنس",
        board=CurriculumBoard.PUNJAB,
        grades=[6, 7, 8, 9, 10],
        description="Study of natural phenomena and scientific principles",
        description_ur="قدرتی مظاہر اور سائنسی اصولوں کا مطالعہ",
        icon="🔬",
        chapters={9: SCIENCE_GRADE_9_CHAPTERS},
    ),
    Subject(
        id="english",
        name="English",
        name_ur="انگریزی",
        board=CurriculumBoard.PUNJAB,
        grades=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        description="English language and literature",
        description_ur="انگریزی زبان اور ادب",
        icon="📚",
        chapters={9: ENGLISH_GRADE_9_CHAPTERS},
    ),
    Subject(
        id="urdu",
        name="Urdu",
        name_ur="اردو",
        board=CurriculumBoard.PUNJAB,
        grades=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        description="Urdu language and literature",
        description_ur="اردو زبان اور ادب",
        icon="✍️",
        chapters={9: URDU_GRADE_9_CHAPTERS},
    ),
]

# ============================================================================
# GENERATE TOPICS FOR ALL GRADES (6-12)
# ============================================================================

def _generate_topics_for_grade(base_topics, source_grade, target_grade):
    """Generate topics for a different grade based on existing topics."""
    generated = []
    for topic in base_topics:
        # Create a new topic ID with the target grade
        new_id = topic.id.replace(f"_{source_grade}_", f"_{target_grade}_")
        new_chapter_id = topic.chapter_id.replace(f"_{source_grade}_", f"_{target_grade}_") if topic.chapter_id else None
        
        # Adjust difficulty based on grade
        if target_grade < source_grade:
            # Lower grades = easier content
            diff = DifficultyLevel.EASY if topic.difficulty == DifficultyLevel.MEDIUM else topic.difficulty
        elif target_grade > source_grade:
            # Higher grades = harder content
            diff = DifficultyLevel.HARD if topic.difficulty == DifficultyLevel.MEDIUM else topic.difficulty
        else:
            diff = topic.difficulty
        
        generated.append(Topic(
            id=new_id,
            name=topic.name,
            name_ur=topic.name_ur,
            chapter_id=new_chapter_id,
            subject_id=topic.subject_id,
            grade=target_grade,
            order=topic.order,
            description=topic.description,
            description_ur=topic.description_ur,
            objectives=topic.objectives,
            prerequisites=[],  # Clear prerequisites for other grades
            estimated_hours=topic.estimated_hours,
            difficulty=diff,
            keywords=topic.keywords,
        ))
    return generated

# Generate topics for grades 6, 7, 8, 10, 11, 12
MATH_GRADE_6_TOPICS = _generate_topics_for_grade(MATH_GRADE_9_TOPICS[:3], 9, 6)
MATH_GRADE_7_TOPICS = _generate_topics_for_grade(MATH_GRADE_9_TOPICS[:3], 9, 7)
MATH_GRADE_8_TOPICS = _generate_topics_for_grade(MATH_GRADE_9_TOPICS[:3], 9, 8)
MATH_GRADE_10_TOPICS = _generate_topics_for_grade(MATH_GRADE_9_TOPICS[:3], 9, 10)
MATH_GRADE_11_TOPICS = _generate_topics_for_grade(MATH_GRADE_9_TOPICS[:3], 9, 11)
MATH_GRADE_12_TOPICS = _generate_topics_for_grade(MATH_GRADE_9_TOPICS[:3], 9, 12)

SCIENCE_GRADE_6_TOPICS = _generate_topics_for_grade(SCIENCE_GRADE_9_TOPICS[:3], 9, 6)
SCIENCE_GRADE_7_TOPICS = _generate_topics_for_grade(SCIENCE_GRADE_9_TOPICS[:3], 9, 7)
SCIENCE_GRADE_8_TOPICS = _generate_topics_for_grade(SCIENCE_GRADE_9_TOPICS[:3], 9, 8)
SCIENCE_GRADE_10_TOPICS = _generate_topics_for_grade(SCIENCE_GRADE_9_TOPICS[:3], 9, 10)
SCIENCE_GRADE_11_TOPICS = _generate_topics_for_grade(SCIENCE_GRADE_9_TOPICS[:3], 9, 11)
SCIENCE_GRADE_12_TOPICS = _generate_topics_for_grade(SCIENCE_GRADE_9_TOPICS[:3], 9, 12)

ENGLISH_GRADE_6_TOPICS = _generate_topics_for_grade(ENGLISH_GRADE_9_TOPICS[:3], 9, 6)
ENGLISH_GRADE_7_TOPICS = _generate_topics_for_grade(ENGLISH_GRADE_9_TOPICS[:3], 9, 7)
ENGLISH_GRADE_8_TOPICS = _generate_topics_for_grade(ENGLISH_GRADE_9_TOPICS[:3], 9, 8)
ENGLISH_GRADE_10_TOPICS = _generate_topics_for_grade(ENGLISH_GRADE_9_TOPICS[:3], 9, 10)
ENGLISH_GRADE_11_TOPICS = _generate_topics_for_grade(ENGLISH_GRADE_9_TOPICS[:3], 9, 11)
ENGLISH_GRADE_12_TOPICS = _generate_topics_for_grade(ENGLISH_GRADE_9_TOPICS[:3], 9, 12)

URDU_GRADE_6_TOPICS = _generate_topics_for_grade(URDU_GRADE_9_TOPICS[:3], 9, 6)
URDU_GRADE_7_TOPICS = _generate_topics_for_grade(URDU_GRADE_9_TOPICS[:3], 9, 7)
URDU_GRADE_8_TOPICS = _generate_topics_for_grade(URDU_GRADE_9_TOPICS[:3], 9, 8)
URDU_GRADE_10_TOPICS = _generate_topics_for_grade(URDU_GRADE_9_TOPICS[:3], 9, 10)
URDU_GRADE_11_TOPICS = _generate_topics_for_grade(URDU_GRADE_9_TOPICS[:3], 9, 11)
URDU_GRADE_12_TOPICS = _generate_topics_for_grade(URDU_GRADE_9_TOPICS[:3], 9, 12)

# ============================================================================
# ALL TOPICS FOR EASY ACCESS
# ============================================================================

ALL_TOPICS = (
    # Grade 6
    MATH_GRADE_6_TOPICS + SCIENCE_GRADE_6_TOPICS + ENGLISH_GRADE_6_TOPICS + URDU_GRADE_6_TOPICS +
    # Grade 7
    MATH_GRADE_7_TOPICS + SCIENCE_GRADE_7_TOPICS + ENGLISH_GRADE_7_TOPICS + URDU_GRADE_7_TOPICS +
    # Grade 8
    MATH_GRADE_8_TOPICS + SCIENCE_GRADE_8_TOPICS + ENGLISH_GRADE_8_TOPICS + URDU_GRADE_8_TOPICS +
    # Grade 9 (original)
    MATH_GRADE_9_TOPICS + SCIENCE_GRADE_9_TOPICS + ENGLISH_GRADE_9_TOPICS + URDU_GRADE_9_TOPICS +
    # Grade 10
    MATH_GRADE_10_TOPICS + SCIENCE_GRADE_10_TOPICS + ENGLISH_GRADE_10_TOPICS + URDU_GRADE_10_TOPICS +
    # Grade 11
    MATH_GRADE_11_TOPICS + SCIENCE_GRADE_11_TOPICS + ENGLISH_GRADE_11_TOPICS + URDU_GRADE_11_TOPICS +
    # Grade 12
    MATH_GRADE_12_TOPICS + SCIENCE_GRADE_12_TOPICS + ENGLISH_GRADE_12_TOPICS + URDU_GRADE_12_TOPICS
)

ALL_CHAPTERS = (
    MATH_GRADE_9_CHAPTERS +
    SCIENCE_GRADE_9_CHAPTERS +
    ENGLISH_GRADE_9_CHAPTERS +
    URDU_GRADE_9_CHAPTERS
)

# ============================================================================
# MAIN DATA EXPORT
# ============================================================================

CURRICULUM_DATA = {
    "subjects": {s.id: s for s in SUBJECTS},
    "chapters": {c.id: c for c in ALL_CHAPTERS},
    "topics": {t.id: t for t in ALL_TOPICS},
    "boards": [b.value for b in CurriculumBoard],
    "grades": list(range(1, 13)),
}
