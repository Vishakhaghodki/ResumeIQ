"""Skill taxonomy. Extend these lists to improve detection."""

SKILLS = [
    # Languages
    "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Rust", "Kotlin", "Swift",
    "PHP", "Ruby", "Scala", "MATLAB", "SQL", "NoSQL", "HTML", "CSS", "Bash", "PowerShell",
    # Web / backend
    "Flask", "Django", "FastAPI", "Spring Boot", "Node.js", "Express.js", "React", "Angular",
    "Vue.js", "Next.js", "Bootstrap", "Tailwind CSS", "jQuery", "REST API", "GraphQL",
    "Microservices", "OOP", "Data Structures", "Algorithms", "System Design",
    # Databases
    "MySQL", "PostgreSQL", "SQLite", "MongoDB", "Redis", "Oracle", "Firebase", "Elasticsearch",
    # Data / AI
    "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "Keras", "OpenCV", "NLP",
    "Machine Learning", "Deep Learning", "Computer Vision", "Data Analysis",
    "Data Visualization", "Matplotlib", "Seaborn", "Tableau", "Power BI", "Excel", "Statistics",
    "Generative AI", "LLM", "LangChain", "Hugging Face", "Apache Spark", "Hadoop", "Kafka",
    "Airflow", "ETL", "Data Engineering",
    # Cloud / DevOps
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "Jenkins", "CI/CD", "Git",
    "GitHub", "GitLab", "Linux", "Nginx", "DevOps", "Ansible",
    # Process / testing
    "Agile", "Scrum", "JIRA", "Unit Testing", "Pytest", "Selenium", "Postman", "JUnit",
    # Other
    "Android", "Flutter", "React Native", "Cybersecurity", "Networking", "IoT",
    "Embedded Systems", "Blockchain", "Web Scraping", "Figma", "UI/UX",
    "Communication", "Leadership", "Teamwork", "Problem Solving",
]

# alias (lowercase) -> canonical skill name
ALIASES = {
    "js": "JavaScript", "ts": "TypeScript", "golang": "Go", "r programming": "R",
    "c programming": "C", "c language": "C", "reactjs": "React", "react.js": "React",
    "vuejs": "Vue.js", "vue": "Vue.js", "angularjs": "Angular", "nodejs": "Node.js",
    "expressjs": "Express.js", "springboot": "Spring Boot", "postgres": "PostgreSQL",
    "mongo": "MongoDB", "sklearn": "Scikit-learn", "scikit learn": "Scikit-learn",
    "ml": "Machine Learning", "natural language processing": "NLP", "k8s": "Kubernetes",
    "amazon web services": "AWS", "google cloud": "GCP", "google cloud platform": "GCP",
    "ci cd": "CI/CD", "cicd": "CI/CD", "restful": "REST API", "restful api": "REST API",
    "restful apis": "REST API", "rest apis": "REST API", "restful services": "REST API",
    "object oriented programming": "OOP", "object-oriented programming": "OOP",
    "dsa": "Data Structures", "microsoft excel": "Excel", "ms excel": "Excel",
    "advanced excel": "Excel", "powerbi": "Power BI", "pyspark": "Apache Spark",
    "large language models": "LLM", "llms": "LLM", "tailwind": "Tailwind CSS",
    "huggingface": "Hugging Face", "unit tests": "Unit Testing", "ui ux": "UI/UX",
    "problem-solving": "Problem Solving", "team work": "Teamwork",
}
