# AWS Landing Zone Accelerator (LZA) Configuration

This repository stores the configuration files for deploying an AWS environment using the [Landing Zone Accelerator on AWS (LZA)](https://aws.amazon.com/solutions/implementations/landing-zone-accelerator-on-aws/) solution.

The LZA helps deploy a cloud foundation aligned with AWS best practices and multiple global compliance frameworks, suitable for managing multi-account environments with highly-regulated workloads.

## Purpose

The primary purpose of this repository is to version control the LZA configuration files and automate the deployment process via a CI/CD pipeline.

## Configuration Files (`config/` directory)

The `config/` directory contains the core YAML files that define your AWS environment setup through the LZA.

*   `accounts-config.yaml`: Defines the AWS accounts within your Organization, including mandatory accounts (Management, LogArchive, Audit) and workload accounts. Specifies their OU placement and email addresses.
*   `global-config.yaml`: Contains global settings like the home region, enabled regions, Control Tower configuration, central logging settings (CloudTrail, CloudWatch Logs), S3/Lambda encryption defaults, cost and usage reports, budget configurations, and service limit increases.
*   `iam-config.yaml`: Defines Identity Center configuration, global IAM policy sets, role sets (like default EC2 roles), IAM groups/users (e.g., break-glass users), and Managed Active Directory setup (if used).
*   `network-config.yaml`: Specifies the network architecture, including VPC definitions (CIDRs, subnets, route tables, internet gateways, NAT gateways), Transit Gateway setup (attachments, route tables, sharing), central network services (IPAM, Network Firewall, Route 53 Resolver endpoints/rules), VPC endpoints (interface and gateway), load balancers, security groups, network ACLs, and certificates.
*   `organization-config.yaml`: Defines the AWS Organizations structure (OUs), Service Control Policies (SCPs) applied to OUs/accounts for guardrails, and tagging/backup policies.
*   `security-config.yaml`: Configures central security services like GuardDuty, Security Hub, Macie, Access Analyzer, default EBS encryption, S3 public access blocks, IAM password policies, and AWS Config recorder settings.

Refer to the official [LZA Configuration Documentation](https://docs.aws.amazon.com/solutions/latest/landing-zone-accelerator-on-aws/configuration-files.html) for detailed schema and parameter information.

## CI/CD Pipeline (GitHub Actions)

This repository uses GitHub Actions (`.github/workflows/lza_config_ci.yaml`) to validate and deploy configuration changes.

### Workflow Triggers

*   **Push events** to `master` or any other branch (affecting files in `config/`, `schema.yaml`, or the workflow itself).
*   **Pull request events** targeting the `master` branch (affecting files in `config/`, `schema.yaml`, or the workflow itself).

### Jobs

1.  **`validate`**:
    *   Runs on every push to any branch and on pull requests targeting `master`.
    *   Checks out the code.
    *   Sets up Python.
    *   Installs `yamale` (a YAML validation tool).
    *   Validates all `*.yaml` files within the `config/` directory against the basic schema defined in `schema.yaml`. This ensures the files are well-formed YAML maps.

2.  **`deploy`**:
    *   Runs **only** on push events to the `master` branch, after the `validate` job succeeds.
    *   Checks out the code.
    *   Configures AWS credentials using secrets.
    *   Creates a zip archive named `aws-accelerator-config.zip` containing all files from the `config/` directory directly at the root of the archive.
    *   Uploads the `aws-accelerator-config.zip` file to the specified S3 bucket and prefix using `aws s3 cp`.
    *   Starts an execution of the specified AWS CodePipeline using `aws codepipeline start-pipeline-execution`. This pipeline is typically the one created by the LZA installer, which consumes the configuration zip file.

### Required GitHub Secrets

To enable the `deploy` job, you must configure the following secrets in your GitHub repository settings (`Settings > Secrets and variables > Actions`):

*   `AWS_OIDC_ROLE_ARN`: The ARN (Amazon Resource Name) of the IAM Role that GitHub Actions will assume via OIDC. This role must be configured in your AWS account to trust GitHub's OIDC provider (`token.actions.githubusercontent.com`) and have permissions to:
    *   Upload to the S3 bucket (`s3:PutObject`).
    *   Start the CodePipeline execution (`codepipeline:StartPipelineExecution`).
    *   Run preflight checks (`config:DescribeComplianceByConfigRule`, `cloudformation:ListStacks`).
*   `AWS_REGION`: The AWS region where your LZA Home Resources (CodePipeline, S3 bucket, Config Rules) reside (e.g., `us-east-1`).
*   `S3_BUCKET`: The name of the S3 bucket where the `aws-accelerator-config.zip` will be uploaded. This is typically the LZA configuration bucket.
*   `S3_KEY_PREFIX`: (Optional) The prefix (folder path) within the S3 bucket where the zip file should be placed. Leave blank or omit if uploading to the root.
*   `CODEPIPELINE_NAME`: The name of the AWS CodePipeline to trigger (usually the LZA pipeline, e.g., `AWSAccelerator-Pipeline`).
*   `LZA_STACK_PREFIX`: The prefix used for your Landing Zone Accelerator CloudFormation stacks (e.g., `AWSAccelerator`), required for the preflight check script.

**Note:** This workflow uses AWS OIDC for authentication, assuming an IAM role via short-lived credentials provided by GitHub Actions. Ensure you have configured the corresponding IAM role with the necessary trust policy and permissions in your AWS account.

## Usage

1.  Clone the repository.
2.  Modify the YAML files in the `config/` directory according to your requirements.
3.  Commit and push your changes to a feature branch.
4.  Create a Pull Request to `master`. The `validate` job will run automatically.
5.  Review and merge the Pull Request.
6.  Upon merging to `master`, the `validate` job runs again, followed by the `deploy` job, which uploads the configuration and triggers the LZA CodePipeline. 