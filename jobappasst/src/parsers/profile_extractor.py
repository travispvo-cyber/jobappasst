"""Extract structured profile data from resume text using Claude API"""

import json
import os
from pathlib import Path
from typing import Dict, Any
from anthropic import Anthropic
import jsonschema


# Load profile schema
SCHEMA_PATH = Path(__file__).parent.parent.parent / "schemas" / "profile_schema.json"


def load_schema() -> Dict[str, Any]:
    """Load the profile JSON schema"""
    with open(SCHEMA_PATH, 'r') as f:
        return json.load(f)


def extract_profile_from_text(resume_text: str, api_key: str | None = None) -> Dict[str, Any]:
    """
    Extract structured profile data from resume text using Claude API.

    Args:
        resume_text: Raw text extracted from resume
        api_key: Anthropic API key (if None, reads from ANTHROPIC_API_KEY env var)

    Returns:
        dict: Structured profile data matching profile_schema.json

    Raises:
        ValueError: If API key is missing or profile extraction fails
        jsonschema.ValidationError: If extracted data doesn't match schema
    """
    # Get API key
    if api_key is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError(
            "Anthropic API key required. "
            "Provide via api_key parameter or ANTHROPIC_API_KEY environment variable"
        )

    # Initialize Claude client
    client = Anthropic(api_key=api_key)

    # Create the prompt for Claude
    prompt = f"""You are a professional resume parser. Extract structured information from the following resume text and return it as a JSON object.

REQUIREMENTS:
1. Extract ALL relevant information
2. Return ONLY valid JSON (no markdown, no explanations)
3. Follow this exact structure:

{{
  "name": "Full name",
  "email": "email@example.com",
  "phone": "phone number",
  "location": "City, State",
  "summary": "Professional summary or objective",
  "skills": [
    {{
      "name": "Skill name",
      "category": "technical|soft|tool|concept",
      "level": "beginner|intermediate|advanced",
      "years": 2.5,
      "context": "Where/how used"
    }}
  ],
  "experience": [
    {{
      "title": "Job title",
      "company": "Company name",
      "industry": "Industry",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM or present",
      "responsibilities": ["List of responsibilities"],
      "accomplishments": ["Key achievements"],
      "skills_used": ["Skills used in this role"]
    }}
  ],
  "education": [
    {{
      "degree": "Degree type",
      "field": "Field of study",
      "institution": "School name",
      "graduation_date": "Year or YYYY-MM"
    }}
  ],
  "certifications": [
    {{
      "name": "Certification name",
      "issuer": "Issuing organization",
      "date": "When obtained"
    }}
  ]
}}

GUIDELINES:
- For skills, infer category (technical/soft/tool/concept) and level based on context
- Estimate years of experience for skills based on work history
- Convert dates to YYYY-MM format
- Extract measurable accomplishments separately from general responsibilities
- If a field is not present in the resume, omit it (except required fields: name, skills, experience)

RESUME TEXT:
{resume_text}

Return ONLY the JSON object, no other text."""

    try:
        # Call Claude API
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            temperature=0,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract the response text
        response_text = response.content[0].text

        # Parse JSON
        try:
            profile_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            # Try to extract JSON from markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                profile_data = json.loads(json_str)
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                profile_data = json.loads(json_str)
            else:
                raise ValueError(f"Failed to parse JSON from Claude response: {str(e)}")

        # Validate against schema
        schema = load_schema()
        jsonschema.validate(instance=profile_data, schema=schema)

        return profile_data

    except jsonschema.ValidationError as e:
        raise jsonschema.ValidationError(
            f"Extracted profile data doesn't match schema: {str(e)}"
        )
    except Exception as e:
        raise Exception(f"Error extracting profile with Claude: {str(e)}")


def validate_profile(profile_data: Dict[str, Any]) -> bool:
    """
    Validate profile data against the schema.

    Args:
        profile_data: Profile data to validate

    Returns:
        bool: True if valid

    Raises:
        jsonschema.ValidationError: If validation fails
    """
    schema = load_schema()
    jsonschema.validate(instance=profile_data, schema=schema)
    return True


# Example usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python profile_extractor.py <resume_text>")
        sys.exit(1)

    # For testing, read text from a file or use command line argument
    text_source = sys.argv[1]

    if Path(text_source).exists():
        with open(text_source, 'r') as f:
            resume_text = f.read()
    else:
        resume_text = text_source

    try:
        profile = extract_profile_from_text(resume_text)
        print(json.dumps(profile, indent=2))
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
