#!/usr/bin/env python3
"""
Pre-tool hook: blocks dangerous shell commands before Claude executes them.
Bootstrap repo has stricter rules — IAM and OIDC operations are especially dangerous.
"""
import json
import sys

try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)

command = payload.get("tool_input", {}).get("command", "")

BLOCKED_PATTERNS = [
    ("terraform apply", "Use CI/CD pipeline for apply operations"),
    ("terraform destroy", "OIDC Provider destruction breaks all dependent repos"),
    ("terraform state rm", "Manual state removal requires explicit authorization"),
    ("terraform state push", "Manual state push requires explicit authorization"),
    ("terraform state mv", "Manual state move requires explicit authorization"),
    ("terraform force-unlock", "Force unlock requires explicit authorization"),
    ("aws iam delete-role", "IAM role deletion requires explicit authorization"),
    ("aws iam put-role-policy", "IAM policy modification requires explicit authorization"),
    ("aws iam attach-role-policy", "IAM policy modification requires explicit authorization"),
    ("aws iam detach-role-policy", "IAM policy modification requires explicit authorization"),
    ("aws iam delete-open-id-connect-provider", "OIDC Provider deletion breaks all CI/CD pipelines"),
    ("aws s3 rb", "S3 bucket removal requires explicit authorization"),
    ("git push --force", "Force push is not allowed"),
    ("git push -f ", "Force push is not allowed"),
    ("git reset --hard", "Hard reset discards uncommitted work"),
]

for pattern, reason in BLOCKED_PATTERNS:
    if pattern in command:
        print(
            json.dumps({
                "decision": "block",
                "reason": f"Blocked: '{pattern}' — {reason}."
            })
        )
        sys.exit(2)

sys.exit(0)
