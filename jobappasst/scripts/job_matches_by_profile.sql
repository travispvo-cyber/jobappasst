
-- Query job matches by profile name (format: "First Last")
SELECT
  p.name AS "Profile Name",
  j.title AS "Job Title",
  jm.matched_skills AS "Match",
  jm.match_score AS "Score",
  j.apply_url AS "URL"
FROM job_matches jm
JOIN profiles p ON p.id = jm.profile_id
JOIN jobs j ON j.id = jm.job_id
WHERE p.name = :profile_name
ORDER BY jm.match_score DESC, jm.scored_at DESC;
'@ | Set-Content -Path "c:\Projects\jobappasst\scripts\job_matches_by_profile.sql" -Encoding ASCII