# AWS Landing Zone Accelerator Configuration (examples)

This directory contains example configuration files for the AWS Landing Zone Accelerator (LZA). These files define the structure, policies, and resources for your AWS multi-account environment.

## Configuration Files Overview

### Core Configuration Files

| File | Purpose |
|------|---------|
| `accounts-config.yaml` | Defines AWS accounts and their organizational unit placement |
| `global-config.yaml` | Contains global settings like enabled regions, logging configuration, and SNS topics |
| `iam-config.yaml` | Configures IAM policies, roles, and permission boundaries |
| `network-config.yaml` | Defines network infrastructure including VPCs, Transit Gateways, and IP address management |
| `organization-config.yaml` | Configures organizational units (OUs) and service control policies (SCPs) |
| `security-config.yaml` | Sets up security services like GuardDuty, Security Hub, and IAM password policies |
| `customizations-config.yaml` | Defines custom resources deployed via CloudFormation |
| `replacements-config.yaml` | Contains variables used across configuration files |

### Supporting Directories

- `custom-config-rules/` - Custom AWS Config rules
- `customizations/` - CloudFormation templates for custom resources
- `dns-firewall-domain-lists/` - Domain lists for DNS firewall rules
- `iam-policies/` - IAM policy documents
- `service-control-policies/` - Service Control Policy (SCP) documents
- `ssm-documents/` - SSM automation documents
- `sso-metadata/` - SSM metadata for Identity Center
- `tagging-policies/` - Resource tagging policies
- `vpc-endpoint-policies/` - VPC endpoint policies

## Key Configuration Components

### Organization Structure

The `organization-config.yaml` file defines the AWS organizational structure with OUs including:
- Security
- Infrastructure
- SomeEnv (with Development, Staging, and Production sub-OUs)
- DataPlatform
- Sandbox

### Accounts

The `accounts-config.yaml` file defines both mandatory accounts (Management, LogArchive, Audit) and workload accounts like Network and SomeEnvProduction.

### Networking

The `network-config.yaml` file configures:
- Transit Gateways for centralized network connectivity
- IP address management (IPAM) for organizing IP address space
- Network Firewall for traffic inspection
- Route53 Resolver for DNS management

### Security Controls

The `security-config.yaml` file enables security services like:
- GuardDuty for threat detection
- Security Hub for security standards compliance
- Macie for sensitive data discovery
- AWS Config for resource compliance

### Service Control Policies

The `service-control-policies/` directory contains SCPs that enforce security guardrails:
- `General-Workload-Policy.json` - Enforces encryption, prevents root account usage
- `Whitelisted-Services.json` - Restricts AWS service usage to an approved list

### IAM Configuration

The `iam-config.yaml` file defines:
- Permission boundaries for developers and platform engineers
- CI/CD roles with appropriate permissions
- IAM policies for secure access

### Customizations

The `customizations-config.yaml` file defines custom resources including:
- GitHub OIDC provider for secure CI/CD integration
- Repository-specific deployment roles

## Variable Replacements

The `replacements-config.yaml` file defines variables used throughout the configuration:
- `AcceleratorPrefix`: Prefix for resource names (e.g., "lza")
- Network CIDR ranges for different environments
- Email addresses for security notifications

## Usage

1. Modify these configuration files to match your organization's requirements
2. Validate your changes using the validation tools described in [LZA_VALIDATION.md](../LZA_VALIDATION.md)
3. Follow the CI/CD workflow described in the main [README.md](../README.md) to deploy your changes

## Best Practices

1. Use version control for all configuration changes
2. Test changes in a development environment before applying to production
3. Follow the principle of least privilege when defining IAM roles and policies
4. Implement network segmentation using Transit Gateways and security groups
5. Enable security services across all accounts
6. Use SCPs to enforce organizational policies

For detailed schema information, refer to the [official LZA documentation](https://docs.aws.amazon.com/solutions/latest/landing-zone-accelerator-on-aws/configuration-files.html).