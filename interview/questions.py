# -*- coding: utf-8 -*-
"""Questions RH standard + fiches de poste."""

STANDARD_RH_QUESTIONS = [
    {
        "id": "STD-RH-001",
        "question": "Tell me about yourself.",
        "ideal_answer": "Hi, I'm [Name]. I'm a software engineer with X years of experience specializing in [skills]. I've worked on [projects] where I [achievement]. I'm passionate about [domain].",
        "keywords": ["experience", "development", "backend", "Java", "Spring Boot"],
        "elements": {
            "nom": ["i'm", "my name", "i am"],
            "poste": ["software engineer", "developer", "analyst"],
            "experience": ["years of experience", "worked", "experience in"],
            "competences": ["java", "python", "spring", "sql"],
            "realisation": ["worked on", "achieved", "improved", "optimized"],
            "motivation": ["looking for", "passionate", "want", "goal"]
        },
        "weight": 0.20,
    },
    {
        "id": "STD-RH-002",
        "question": "Why are you interested in this position?",
        "ideal_answer": "It matches my skills in [domain] and I admire [company]. I want to contribute to [project].",
        "keywords": ["skills", "company", "projects"],
        "elements": {
            "entreprise": ["company", "your team", "your projects"],
            "poste": ["position", "role", "job"],
            "competences": ["skills", "match", "fit"],
            "motivation": ["excited", "interested", "passionate"],
            "projet": ["contribute", "grow", "learn"]
        },
        "weight": 0.20,
    },
    {
        "id": "STD-RH-003",
        "question": "What is your biggest technical challenge?",
        "ideal_answer": "My biggest challenge was [problem]. I analyzed [approach] and achieved [result].",
        "keywords": ["challenge", "problem", "solution", "result"],
        "elements": {
            "contexte": ["project", "team", "application"],
            "probleme": ["problem", "issue", "challenge"],
            "action": ["analyzed", "implemented", "solved"],
            "resultat": ["reduced", "improved", "achieved"],
            "apprentissage": ["learned", "realized", "understood"]
        },
        "weight": 0.20,
    },
    {
        "id": "STD-RH-004",
        "question": "How do you handle disagreements with colleagues?",
        "ideal_answer": "I listen first, then we find a compromise together.",
        "keywords": ["listen", "perspective", "solution", "together"],
        "elements": {
            "ecoute": ["listen", "understand", "hear"],
            "dialogue": ["discuss", "talk", "communicate"],
            "compromis": ["compromise", "agree", "find"],
            "solution": ["solution", "resolve", "fix"],
            "respect": ["respect", "professional", "calm"]
        },
        "weight": 0.20,
    },
    {
        "id": "STD-RH-005",
        "question": "Where do you see yourself in 3 years?",
        "ideal_answer": "As a [role] having developed [skills].",
        "keywords": ["tech lead", "mentoring", "architecture", "grow"],
        "elements": {
            "objectif": ["senior", "lead", "expert", "manager"],
            "competences": ["skills", "learn", "develop"],
            "entreprise": ["company", "here", "your team"],
            "plan": ["plan", "path", "step"],
            "motivation": ["passionate", "want", "goal"]
        },
        "weight": 0.20,
    },
]


job_descriptions = {
    "Software Engineer": "Java, Python, OOP, Spring Boot, REST APIs, SQL, Git",
    "Data Scientist": "Python, ML, Deep Learning, Statistics, SQL, TensorFlow, PyTorch",
    "QA Analyst": "Testing, Selenium, Cypress, API testing, CI/CD, Bug tracking",
}


if __name__ == "__main__":
    print(f"{len(STANDARD_RH_QUESTIONS)} questions chargees.")
    for q in STANDARD_RH_QUESTIONS:
        print(f"  {q['id']} - {q['question']}")
    print(f"{len(job_descriptions)} profils charges : {list(job_descriptions.keys())}")