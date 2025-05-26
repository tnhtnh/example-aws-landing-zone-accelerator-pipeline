# LZA Validation Guide

This document provides guidance on validating your Landing Zone Accelerator (LZA) configuration before deployment.

## Why Validate Your Configuration?

Validating your LZA configuration locally offers several benefits:

- **Catch errors early**: Identify syntax and configuration issues before committing to your repository
- **Save time**: Avoid waiting for CI/CD pipeline failures that could take up to 90 minutes to execute
- **Reduce risk**: Ensure your infrastructure changes are valid before they reach production
- **Improve quality**: Maintain consistent standards across your AWS environment

## Local YAML Validation

YAML validation ensures your configuration files have correct syntax and follow style guidelines:

```bash
# Install yamllint (if not already installed)
pip install yamllint

# Run linter
yamllint config/
```

This checks all YAML files in the `config/` directory for syntax errors and style issues, helping to catch common mistakes before they cause deployment failures.

## Local Preflight Checks

Preflight checks verify that your AWS environment is in a healthy state before attempting to deploy LZA changes:

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials in your environment
# (e.g., using environment variables or aws configure)

# Set required environment variables
export AWS_REGION="your-aws-region"
# export CT_HOME_REGION="your-ct-home-region" # If different from AWS_REGION
export LZA_STACK_PREFIX="your-lza-stack-prefix"

# Run the script (adjust path if necessary)
python lza_preflight_check.py --prefix "$LZA_STACK_PREFIX"
```

### What the Preflight Checks Verify

1. **Failed CloudFormation Stacks**: Identifies any CloudFormation stacks with your LZA prefix that are in a failed state (e.g., `CREATE_FAILED`, `ROLLBACK_COMPLETE`)
   
2. **Control Tower Landing Zone Status**: Verifies that AWS Control Tower is enabled and that the Landing Zone status is `ACTIVE`. It also warns if the Landing Zone is drifted (`DRIFTED`) or not up-to-date with the latest version.

Running these checks locally helps you identify potential issues that would cause your deployment to fail, saving time and reducing frustration during the deployment process.