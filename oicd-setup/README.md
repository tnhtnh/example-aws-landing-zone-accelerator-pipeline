# GitHub Actions OIDC Setup for LZA Deployment

This CloudFormation template automates the setup of the necessary AWS IAM resources to allow your GitHub Actions workflow to securely authenticate with AWS using OpenID Connect (OIDC) and deploy Landing Zone Accelerator (LZA) configuration changes.

## Purpose

The template creates:

1.  **IAM OIDC Identity Provider:** Establishes trust between your AWS account and GitHub Actions (`token.actions.githubusercontent.com`).
2.  **IAM Role:** Creates a dedicated IAM role that GitHub Actions workflows from your specific repository can assume. This role is granted the minimum necessary permissions to:
    *   Run LZA preflight checks (`config:DescribeComplianceByConfigRule`, `cloudformation:ListStacks`).
    *   Upload the `aws-accelerator-config.zip` file to the designated LZA S3 bucket (`s3:PutObject`).
    *   Trigger the LZA CodePipeline (`codepipeline:StartPipelineExecution`).

Using OIDC is more secure than storing long-lived AWS access keys as GitHub secrets because it uses short-lived credentials obtained automatically by the workflow.

## Prerequisites

*   An AWS account.
*   Permissions to create IAM OIDC Providers and IAM Roles/Policies within that account.
*   The name of your LZA S3 configuration bucket.
*   The full ARN of your LZA CodePipeline.

## Deployment

You can deploy this stack using the AWS Management Console or the AWS CLI.

**Using AWS CLI:**

```bash
aws cloudformation deploy \
    --template-file github_oidc_setup.yaml \
    --stack-name GitHubOidcForLzaDeploy \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
    --parameter-overrides \
        GitHubOrg=<YourGitHubOrgName> \
        GitHubRepo=<YourGitHubRepoName> \
        LzaS3BucketName=<YourLzaConfigBucketName> \
        LzaCodePipelineArn=<YourLzaPipelineArn> \
        # IamRoleName=OptionalRoleName # Optional: Override default role name if needed
```

Replace the placeholder values (`<...>`) with your specific information.

**Parameters:**

*   `GitHubOrg` (Required): Your GitHub organization or username (e.g., `my-org`).
*   `GitHubRepo` (Required): Your GitHub repository name (e.g., `lza-config-repo`).
*   `LzaS3BucketName` (Required): The name of the S3 bucket used by LZA for configuration (e.g., `my-lza-config-bucket-12345`).
*   `LzaCodePipelineArn` (Required): The full ARN of the LZA CodePipeline (e.g., `arn:aws:codepipeline:us-east-1:123456789012:MyLzaPipeline`).
*   `IamRoleName` (Optional): The name for the created IAM role. Defaults to `GitHubActionsLzaDeployRole`.

## Outputs

*   `OidcRoleArn`: The ARN of the created IAM role.

## Post-Deployment

1.  After the stack successfully deploys, copy the `OidcRoleArn` value from the CloudFormation stack outputs.
2.  Go to your GitHub repository settings: `Settings > Secrets and variables > Actions`.
3.  Create a new repository secret named `AWS_OIDC_ROLE_ARN`.
4.  Paste the copied IAM Role ARN as the value for the secret.

Your GitHub Actions workflow (`.github/workflows/lza_config_ci.yaml`) should now be able to assume this role and interact with AWS securely.

## Security Note

The IAM role's trust policy restricts assumption to only the specified GitHub repository (`repo:<GitHubOrg>/<GitHubRepo>:*`). You can further restrict this to specific branches (e.g., `repo:<GitHubOrg>/<GitHubRepo>:ref:refs/heads/master`) by modifying the `StringLike` condition in the `AssumeRolePolicyDocument` within the CloudFormation template if needed. 