# Getting Started

## 1. Deploy the Landing Zone Accelerator

Deploy the AWS Landing Zone Accelerator by following the official documentation:
https://aws.amazon.com/solutions/implementations/landing-zone-accelerator-on-aws/

Ensure that you have completed all prerequisites as outlined here:
https://docs.aws.amazon.com/solutions/latest/landing-zone-accelerator-on-aws/prerequisites.html

When launching the stack (https://docs.aws.amazon.com/solutions/latest/landing-zone-accelerator-on-aws/step-1.-launch-the-stack.html), it is recommended to use the "Enable Approval Stage" option.

## 2. Identify Key Resources

After successful deployment, identify and note down:
- The S3 bucket name created for your Landing Zone configuration
- The CodePipeline URL for your Landing Zone deployment

## 3. Deploy OIDC Setup

Deploy the OIDC setup for GitHub integration by following the instructions in the `oicd-setup/README.md` file.

## 4. Download and Extract Initial Configuration

1. Download your initial Landing Zone configuration ZIP file from the S3 bucket identified in step 2
2. Extract the contents of the ZIP file
3. Save the extracted configuration files in the `config` directory of this repository

## 5. Set Up GitHub Environment and Secrets

1. In your GitHub repository, go to Settings > Environments > New environment
2. Create environments for your deployment stages (e.g., "development", "production")
3. Add the following secrets to your environments:
   - `AWS_OIDC_ROLE_ARN`: The ARN of the IAM role created during OIDC setup
   - Any other environment-specific secrets required for your workflow

## 6. Configure Branch Protection

1. Go to Settings > Branches > Add rule
2. Set up protection for your main branch:
   - Require pull request reviews before merging
   - Require status checks to pass before merging
   - Require branches to be up to date before merging
   - Include administrators in these restrictions

## 7. Recommended Workflow

For making changes to your Landing Zone configuration:

1. Create a new feature branch from main
2. Make your configuration changes in the branch
3. Create a pull request back to main
4. After review and approval, merge the PR to main
5. The CI/CD pipeline will automatically execute from main, deploying your changes to AWS