"""Skill taxonomy and normalization for matching"""

from typing import List, Set


# Skill synonym mappings
SKILL_SYNONYMS = {
    # Programming languages
    "python": ["python3", "py", "python programming"],
    "javascript": ["js", "ecmascript", "node.js", "nodejs"],
    "sql": ["structured query language", "t-sql", "pl/sql", "mysql", "postgresql", "postgres"],

    # Data tools
    "tableau": ["tableau desktop", "tableau server"],
    "power bi": ["powerbi", "microsoft power bi", "power-bi"],
    "excel": ["microsoft excel", "ms excel", "spreadsheets"],
    "snowflake": ["snowflake data warehouse"],
    "dbt": ["data build tool", "dbt-core"],

    # Cloud platforms
    "aws": ["amazon web services", "amazon aws"],
    "azure": ["microsoft azure", "azure cloud"],
    "gcp": ["google cloud", "google cloud platform"],

    # Concepts
    "data engineering": ["data engineer", "data pipeline", "etl"],
    "data science": ["data scientist", "machine learning", "ml"],
    "business intelligence": ["bi", "business analytics"],
    "cybersecurity": ["cyber security", "information security", "infosec"],

    # Healthcare specific
    "epic": ["epic systems", "epic emr", "epic ehr"],
    "cpt": ["cpt codes", "current procedural terminology"],
    "icd": ["icd-10", "icd codes", "international classification of diseases"],
}


def normalize_skill(skill: str) -> str:
    """
    Normalize a skill name to its canonical form.

    Args:
        skill: Skill name to normalize

    Returns:
        str: Normalized skill name (lowercase, trimmed)
    """
    return skill.lower().strip()


def find_skill_synonyms(skill: str) -> Set[str]:
    """
    Find all synonyms for a given skill.

    Args:
        skill: Skill name

    Returns:
        set: Set of skill synonyms (including the original)
    """
    normalized = normalize_skill(skill)

    # Check if skill is a key
    if normalized in SKILL_SYNONYMS:
        synonyms = {normalized}
        synonyms.update(SKILL_SYNONYMS[normalized])
        return synonyms

    # Check if skill is in any synonym list
    for canonical, synonym_list in SKILL_SYNONYMS.items():
        if normalized in synonym_list or normalized == canonical:
            result = {canonical}
            result.update(synonym_list)
            return result

    # No synonyms found, return just the skill
    return {normalized}


def skills_match(skill1: str, skill2: str) -> bool:
    """
    Check if two skills are equivalent (including synonyms).

    Args:
        skill1: First skill name
        skill2: Second skill name

    Returns:
        bool: True if skills match
    """
    synonyms1 = find_skill_synonyms(skill1)
    synonyms2 = find_skill_synonyms(skill2)

    # Check for any overlap
    return bool(synonyms1 & synonyms2)


def extract_matched_skills(profile_skills: List[str], job_requirements: List[str]) -> List[str]:
    """
    Find skills from profile that match job requirements.

    Args:
        profile_skills: List of skills from profile
        job_requirements: List of requirements from job

    Returns:
        list: List of matched skills
    """
    matched = []

    for profile_skill in profile_skills:
        profile_syns = find_skill_synonyms(profile_skill)

        for req in job_requirements:
            req_normalized = normalize_skill(req)
            # Check if any synonym appears in the requirement text
            if any(syn in req_normalized for syn in profile_syns):
                if profile_skill not in matched:
                    matched.append(profile_skill)
                break

    return matched


# Example usage
if __name__ == "__main__":
    # Test skill matching
    print("Skill matching examples:")
    print(f"'Python' matches 'python3': {skills_match('Python', 'python3')}")
    print(f"'SQL' matches 'PostgreSQL': {skills_match('SQL', 'PostgreSQL')}")
    print(f"'Power BI' matches 'Microsoft Power BI': {skills_match('Power BI', 'Microsoft Power BI')}")
    print()

    # Test synonym finding
    print(f"Synonyms for 'Python': {find_skill_synonyms('Python')}")
    print(f"Synonyms for 'AWS': {find_skill_synonyms('AWS')}")
    print()

    # Test skill extraction
    profile_skills = ["Python", "SQL", "Tableau", "AWS"]
    job_reqs = ["5+ years Python experience", "Strong SQL skills", "Experience with cloud platforms"]
    matched = extract_matched_skills(profile_skills, job_reqs)
    print(f"Profile skills: {profile_skills}")
    print(f"Job requirements: {job_reqs}")
    print(f"Matched skills: {matched}")
