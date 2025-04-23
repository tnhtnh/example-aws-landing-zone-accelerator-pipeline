# AWS Preflight Checks

This project contains a Python script and associated tests to perform preflight checks against an AWS environment before potential deployments or operations.

## Checks Performed

1.  **Failed CloudFormation Stacks:** Checks for any CloudFormation stacks in a specified AWS region that are in a failed state (e.g., `CREATE_FAILED`, `ROLLBACK_COMPLETE`, etc.) and match a defined prefix.
    *   Default Prefix: `AWSAccelerator` (can be overridden).
2.  **Control Tower Landing Zone Status:** Checks if AWS Control Tower is enabled and, if so, verifies that the Landing Zone status is `ACTIVE`. It also logs warnings if the Landing Zone is drifted (`DRIFTED`) or not up-to-date with the latest version.
    *   **Note:** This check verifies the status of the Landing Zone resource itself, not the detailed compliance status of every account and OU against all Control Tower controls. A comprehensive compliance check would typically involve more complex queries against AWS Config or Security Hub, likely within the AWS Audit account.

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── preflight.yml  # GitHub Actions workflow
├── preflight_checks/
│   ├── __init__.py
│   └── aws_checks.py    # Core checking logic
├── tests/
│   ├── __init__.py
│   └── test_aws_checks.py # Unit tests
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Prerequisites

*   Python 3.9+
*   AWS Credentials configured (e.g., via environment variables, IAM role) with necessary permissions:
    *   `cloudformation:ListStacks`
    *   `controltower:ListLandingZones`
    *   `controltower:GetLandingZone`

## Usage

### Local Execution

1.  **Install Dependencies:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate # or .venv\Scripts\activate on Windows
    pip install -r requirements.txt
    ```

2.  **Configure AWS Credentials:** Ensure your environment is configured with valid AWS credentials (e.g., set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, or use an instance profile/role).

3.  **Set Environment Variables (Optional):**
    *   `AWS_REGION`: (Required) The AWS region to run the checks in (e.g., `us-east-1`, `eu-west-2`). This is used for the CloudFormation check and as the default for the Control Tower check.
    *   `CT_HOME_REGION`: (Optional) The AWS region where your Control Tower Landing Zone is homed. Defaults to the value of `AWS_REGION` if not set. Required if your Control Tower home region differs from the `AWS_REGION` you want to check CloudFormation stacks in.
    *   `STACK_PREFIX`: (Optional) The prefix for CloudFormation stacks to check for failures. Defaults to `AWSAccelerator`.

4.  **Run Checks:**
    ```bash
    # Example:
    export AWS_REGION="eu-west-1"
    # export CT_HOME_REGION="us-east-1" # If different
    # export STACK_PREFIX="MyProject-" # If different

    python -m preflight_checks.aws_checks
    ```
    The script will exit with code `0` if all checks pass, and `1` if any check fails or an error occurs.

### GitHub Actions

The `.github/workflows/preflight.yml` workflow automates these checks, typically on pull requests or manually via `workflow_dispatch`.

*   **Authentication:** Uses AWS OIDC for secure, short-lived credentials. You need to configure an IAM Role in your AWS account with the necessary permissions and establish a trust relationship with GitHub Actions.
*   **Configuration:**
    *   Update the `role-to-assume` parameter in the workflow file with the ARN of your IAM role.
    *   The `AWS_REGION` and `CT_HOME_REGION` are set as environment variables in the workflow. You can modify these defaults.
    *   The `STACK_PREFIX` can be overridden using GitHub repository secrets or variables (see commented-out examples in the workflow file).

## Running Tests

Unit tests using `pytest` and `moto` are included.

1.  **Install Test Dependencies (if not already done):**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run Tests with Coverage:**
    ```bash
    pytest tests/ --cov=preflight_checks --cov-report=term-missing
    ```

    To generate an XML coverage report (e.g., for CI integration):
    ```bash
    pytest tests/ --cov=preflight_checks --cov-report=xml
    ```

## Future Enhancements

*   **Detailed Control Tower Compliance:** Implement checks against AWS Config or Security Hub (likely requiring execution within the Audit account or cross-account permissions) to verify individual account/OU compliance against specific controls.
*   **More Granular Error Handling:** Refine error handling for specific AWS API exceptions.
*   **Configurable Failure Conditions:** Allow configuration for whether Landing Zone drift or outdated versions should cause the check to fail (currently they only log warnings). 