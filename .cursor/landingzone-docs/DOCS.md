
# AWS Landing Zone Accelerator Configuration Schema Reference

This document provides a comprehensive schema reference for the AWS Landing Zone Accelerator (LZA) configuration files. Each section details the available configuration options, data types, and descriptions for the respective YAML configuration files.

## Table of Contents

- [accounts-config.yaml](#accounts-configyaml)
- [global-config.yaml](#global-configyaml)
- [iam-config.yaml](#iam-configyaml)
- [network-config.yaml](#network-configyaml)
- [organization-config.yaml](#organization-configyaml)
- [security-config.yaml](#security-configyaml)
- [customizations-config.yaml](#customizations-configyaml)

---

## accounts-config.yaml

This file defines the accounts structure within AWS Organizations and their organization unit (OU) placement.

### Schema

```yaml
# Root level properties
mandatoryAccounts: MandatoryAccount[]
workloadAccounts: WorkloadAccount[]
accountIds: AccountId[]
organizationalUnits: OrganizationalUnit[]
```

### MandatoryAccount

Core accounts required for AWS Control Tower and Landing Zone.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the account. For mandatory accounts, must be one of: Management, LogArchive, or Audit. |
| description | string | Yes | Description of the account's purpose. |
| email | string | Yes | Email address associated with the account. Must be unique across AWS. |
| organizationalUnit | string | Yes | The organizational unit the account belongs to. |
| warm | boolean | No | If true, account is considered already present. Default: false. |
| rootEmail | string | No | The email address used for the root user during account provisioning. |
| controltower | boolean | No | Defines if Control Tower should be used to provision this account. Default: matches the global control tower configuration. |
| tags | Tag[] | No | Array of tags to apply to the account. |
| warm | boolean | No | When true, the solution expects the account to already exist in the organization. Default: false |

### WorkloadAccount

Additional accounts for workloads.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the account. |
| description | string | Yes | Description of the account's purpose. |
| email | string | Yes | Email address associated with the account. Must be unique across AWS. |
| organizationalUnit | string | Yes | The organizational unit the account belongs to. |
| warm | boolean | No | If true, account is considered already present. Default: false. |
| rootEmail | string | No | The email address used for the root user during account provisioning. |
| controltower | boolean | No | Defines if Control Tower should be used to provision this account. Default: matches the global control tower configuration. |
| tags | Tag[] | No | Array of tags to apply to the account. |
| warm | boolean | No | When true, the solution expects the account to already exist in the organization. Default: false |

### AccountId

Maps a previously provisioned account name to its AWS account ID.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| email | string | Yes | Email address associated with the account. |
| accountId | string | Yes | AWS account ID. |

### Tag

Defines a resource tag.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| key | string | Yes | The tag key. |
| value | string | Yes | The tag value. |

---

## global-config.yaml

This file contains global settings for the Landing Zone Accelerator.

### Schema

```yaml
# Root level properties
homeRegion: string
enabledRegions: string[]
managementAccountAccessRole: string
cloudwatchLogRetentionInDays: number
terminationProtection: boolean
controlTower: ControlTowerConfig
logging: LoggingConfig
snsTopics: SnsTopicConfig
tags: Tag[]
reports: ReportsConfig
cdkOptions: CdkOptions
limits: LimitsConfig
globalReplacements: GlobalReplacement[]
externalLandingZoneResources: ExternalLandingZoneResourcesConfig
```

### ControlTowerConfig

Configures AWS Control Tower settings.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| enable | boolean | Yes | Whether AWS Control Tower is enabled. |
| landingZone | LandingZoneConfig | No | Landing Zone configuration. |
| controls | Control[] | No | Control Tower controls to enable. |

### LandingZoneConfig

Control Tower Landing Zone configuration.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| version | string | No | Version of Control Tower Landing Zone. |
| logging | ControlTowerLoggingConfig | No | Configures Control Tower logging settings. |
| security | ControlTowerSecurityConfig | No | Configures Control Tower security settings. |

### ControlTowerLoggingConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| loggingBucketRetentionDays | number | No | Retention days for log buckets. |
| accessLoggingBucketRetentionDays | number | No | Retention days for access log buckets. |
| organizationTrail | boolean | No | If true, deploys an organization trail. |

### ControlTowerSecurityConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| enableIdentityCenterAccess | boolean | No | Whether to enable IAM Identity Center access. |

### LoggingConfig

Configures centralized logging.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| account | string | Yes | Account to centralized logging. |
| cloudtrail | CloudTrailConfig | No | CloudTrail configuration. |
| sessionManager | SessionManagerConfig | No | Session Manager logging configuration. |
| runtimeConfig | ConfigRuntimeConfig | No | Config runtime configuration. |

### CloudTrailConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| enable | boolean | Yes | Whether CloudTrail is enabled. |
| organizationTrail | boolean | Yes | If true, deploys an organization trail. |
| organizationTrailSettings | OrganizationTrailSettings | No | Organization trail settings. |
| accountTrails | AccountTrailConfig[] | No | Account-specific trails. |

### OrganizationTrailSettings

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| multiRegionTrail | boolean | No | Enable multi-region trail. Default: true. |
| globalServiceEvents | boolean | No | Include global service events. Default: true. |
| managementEvents | boolean | No | Log management events. Default: true. |
| s3DataEvents | boolean | No | Log S3 data events. Default: false. |
| lambdaDataEvents | boolean | No | Log Lambda data events. Default: false. |
| sendToCloudWatchLogs | boolean | No | Send logs to CloudWatch Logs. Default: true. |
| apiErrorRateInsight | boolean | No | Enable CloudTrail Insights for API error rates. Default: false. |
| apiCallRateInsight | boolean | No | Enable CloudTrail Insights for API call rates. Default: false. |

### AccountTrailConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the trail. |
| regions | string[] | Yes | Regions to enable the trail in. |
| deploymentTargets | DeploymentTargets | Yes | Accounts to deploy the trail to. |
| settings | AccountTrailSettings | Yes | Trail-specific settings. |

### SessionManagerConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| sendToCloudWatchLogs | boolean | No | Send Session Manager logs to CloudWatch. |
| sendToS3 | boolean | No | Send Session Manager logs to S3. |
| attachPolicyToIamRoles | string[] | No | IAM roles to attach Session Manager policy to. |
| excludeAccounts | string[] | No | Accounts to exclude from Session Manager logging. |
| lifecycleRules | LifecycleRule[] | No | S3 lifecycle rules for Session Manager logs. |

### SnsTopicConfig

Configures SNS topics for notifications.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| deploymentTargets | DeploymentTargets | Yes | Accounts/OUs to deploy SNS topics to. |
| topics | SnsTopic[] | Yes | SNS topics to create. |

### SnsTopic

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the SNS topic. |
| emailAddresses | string[] | Yes | Email addresses to subscribe to the topic. |

### ReportsConfig

Configures Cost and Usage reports.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| costAndUsageReport | CostAndUsageReportConfig | Yes | Cost and Usage Report configuration. |

### CostAndUsageReportConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| additionalSchemaElements | string[] | No | Additional schema elements to include. |
| compression | string | No | Compression type. Default: Parquet. |
| format | string | No | Report format. Default: Parquet. |
| reportName | string | No | Name of the report. Default: accelerator-cur. |
| s3Prefix | string | No | S3 prefix for the report. Default: cur. |
| timeUnit | string | No | Time unit for the report. Default: DAILY. |
| reportVersioning | string | No | Report versioning. Default: OVERWRITE_REPORT. |

### CdkOptions

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| centralizeBuckets | boolean | No | Centralize S3 buckets in home region (true) or create in each region (false). Default: true. |
| useManagementAccessRole | boolean | No | Use AWSControlTowerExecution role for CDK deployments. Default: false. |

### LimitsConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| lambda | LambdaLimitsConfig | No | Lambda quotas configuration. |

### LambdaLimitsConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| concurrency | number | No | Lambda concurrency limit. |

### GlobalReplacement

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| key | string | Yes | Variable name to replace. |
| value | string | Yes | Value to replace with. |
| type | string | Yes | Data type (String, Number, Boolean, etc.). |

### ExternalLandingZoneResourcesConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| certificateAttributes | CertificateAttributes[] | No | External certificate attributes. |

### CertificateAttributes

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name for the certificate reference. |
| arn | string | Yes | ARN of the external certificate. |
| region | string | Yes | Region where the certificate is located. |

---

## iam-config.yaml

This file defines IAM configurations, including roles, users, groups, and policies.

### Schema

```yaml
# Root level properties
policySets: PolicySet[]
roleSets: RoleSet[]
groupSets: GroupSet[]
userSets: UserSet[]
managedPolicySets: ManagedPolicySet[]
identityCenter: IdentityCenterConfig
```

### PolicySet

Set of IAM policies to deploy.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| deploymentTargets | DeploymentTargets | Yes | Accounts/OUs to deploy policies to. |
| policies | Policy[] | Yes | Policies to deploy. |

### Policy

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the policy. |
| description | string | No | Description of the policy. |
| policy | string | Yes | Path to the policy JSON file or inline JSON. |
| tags | Tag[] | No | Tags to apply to the policy. |

### RoleSet

Set of IAM roles to deploy.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| deploymentTargets | DeploymentTargets | Yes | Accounts/OUs to deploy roles to. |
| roles | Role[] | Yes | Roles to deploy. |

### Role

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the role. |
| assumedBy | AssumedBy[] | Yes | Principals that can assume this role. |
| policies | RolePolicies | No | Policies to attach to the role. |
| boundaryPolicy | string | No | Permission boundary policy to apply. |
| instanceProfile | boolean | No | Create an instance profile for this role. Default: false. |
| tags | Tag[] | No | Tags to apply to the role. |

### AssumedBy

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| type | string | Yes | Principal type: 'service', 'account', or 'provider'. |
| principal | string | Yes | Principal identifier (service name, account ID, or provider ARN). |

### RolePolicies

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| awsManaged | string[] | No | AWS-managed policies to attach. |
| customerManaged | string[] | No | Customer-managed policies to attach. |

### GroupSet

Set of IAM groups to deploy.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| deploymentTargets | DeploymentTargets | Yes | Accounts/OUs to deploy groups to. |
| groups | Group[] | Yes | Groups to deploy. |

### Group

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the group. |
| policies | GroupPolicies | No | Policies to attach to the group. |

### GroupPolicies

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| awsManaged | string[] | No | AWS-managed policies to attach. |
| customerManaged | string[] | No | Customer-managed policies to attach. |

### UserSet

Set of IAM users to deploy.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| deploymentTargets | DeploymentTargets | Yes | Accounts/OUs to deploy users to. |
| users | User[] | Yes | Users to deploy. |

### User

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| username | string | Yes | Username for the IAM user. |
| passwordPolicy | UserPasswordPolicy | No | Password policy overrides for this user. |
| group | string | No | Group to add the user to. |
| boundaryPolicy | string | No | Permission boundary policy to apply. |

### UserPasswordPolicy

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| passwordResetRequired | boolean | No | Whether user must reset password on next login. |

### ManagedPolicySet

Set of managed policies to deploy.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| deploymentTargets | DeploymentTargets | Yes | Accounts/OUs to deploy managed policies to. |
| policies | ManagedPolicy[] | Yes | Managed policies to deploy. |

### ManagedPolicy

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the managed policy. |
| path | string | No | Path for the managed policy. Default: '/'. |
| policy | string | Yes | JSON policy document or path to policy file. |

### IdentityCenterConfig

AWS IAM Identity Center configuration.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name identifier for the Identity Center instance. |
| delegatedAdminAccount | string | Yes | Account to use as Identity Center delegated administrator. |
| identityCenterPermissionSets | IdentityCenterPermissionSet[] | No | Permission sets to create in Identity Center. |
| identityCenterAssignments | IdentityCenterAssignment[] | No | Assignments of permission sets to principals. |

### IdentityCenterPermissionSet

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the permission set. |
| policies | IdentityCenterPermissionSetPolicy | No | Policies to attach to the permission set. |
| sessionDuration | string | No | Session duration in ISO-8601 format. Default: PT8H. |

### IdentityCenterPermissionSetPolicy

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| awsManaged | string[] | No | AWS-managed policies to attach. |
| customerManaged | string[] | No | Customer-managed policy references to attach. |
| inlinePolicy | string | No | Inline policy document or path to policy file. |
| permissions | string | No | Reference to a set of AWS-managed application permissions. |

### IdentityCenterAssignment

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| permissionSetName | string | Yes | Name of the permission set to assign. |
| principalId | string | Yes | ID of the principal (user or group) to assign. |
| principalType | string | Yes | Type of principal: 'USER' or 'GROUP'. |
| principalName | string | No | Name of the principal (for documentation). |
| deploymentTargets | DeploymentTargets | Yes | Accounts/OUs to assign the permission set to. |

---

## network-config.yaml

This file defines networking configurations, including VPCs, Transit Gateways, and network services.

### Schema

```yaml
# Root level properties
defaultVpc: DefaultVpcConfig
vpcs: Vpc[]
vpcTemplates: VpcTemplate[]
vpcFlowLogs: VpcFlowLogsConfig
centralNetworkServices: CentralNetworkServicesConfig
transitGateways: TransitGateway[]
routeTables: RouteTable[]
endpointPolicies: EndpointPolicy[]
```

### DefaultVpcConfig

Configures the default VPC in each region.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| delete | boolean | No | Whether to delete the default VPC. Default: false. |
| excludeAccounts | string[] | No | Accounts to exclude from default VPC deletion. |
| deploymentTargets | DeploymentTargets | No | Specific targets to apply default VPC actions to. |

### Vpc

Defines a VPC configuration.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the VPC. |
| account | string | Yes | Account to deploy the VPC to. |
| region | string | Yes | Region to deploy the VPC to. |
| cidrs | string[] | Yes | CIDR blocks for the VPC. |
| internetGateway | boolean | No | Create an internet gateway. Default: false. |
| enableDnsHostnames | boolean | No | Enable DNS hostnames. Default: true. |
| enableDnsSupport | boolean | No | Enable DNS support. Default: true. |
| instanceTenancy | string | No | Instance tenancy setting. Default: 'default'. |
| routeTables | RouteTable[] | Yes | Route tables for the VPC. |
| subnets | Subnet[] | Yes | Subnets within the VPC. |
| natGateways | NatGateway[] | No | NAT gateways for the VPC. |
| securityGroups | SecurityGroup[] | No | Security groups for the VPC. |
| vpcFlowLogs | VpcFlowLog | No | VPC flow log configuration. |
| networkAcls | NetworkAcl[] | No | Network ACLs for the VPC. |
| gatewayEndpoints | GatewayEndpoint | No | Gateway endpoints to create. |
| interfaceEndpoints | InterfaceEndpoint | No | Interface endpoints to create. |
| queryLogs | string[] | No | Route 53 query log configuration references. |
| useCentralEndpoints | boolean | No | Use centralized interface endpoints. Default: false. |
| transitGatewayAttachments | TransitGatewayAttachment[] | No | Transit Gateway attachments. |
| virtualPrivateGateways | VirtualPrivateGateway[] | No | Virtual Private Gateways to attach. |
| tags | Tag[] | No | Tags to apply to the VPC. |
| defaultSecurityGroupRulesDeletion | boolean | No | Delete default security group rules. Default: false. |

### RouteTable

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the route table. |
| routes | Route[] | No | Routes in the route table. |
| tags | Tag[] | No | Tags to apply to the route table. |

### Route

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the route (for identification). |
| destination | string | No | Destination CIDR block for the route. |
| destinationPrefixList | string | No | Destination prefix list ID. |
| type | string | Yes | Route type: 'transitGateway', 'natGateway', 'internetGateway', etc. |
| target | string | No | Target identifier (TGW ID, NAT gateway name, etc.) |

### Subnet

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the subnet. |
| availabilityZone | string | Yes | Availability zone for the subnet. |
| routeTable | string | Yes | Route table to associate with the subnet. |
| ipv4CidrBlock | string | Yes | IPv4 CIDR block for the subnet. |
| mapPublicIpOnLaunch | boolean | No | Assign public IP on launch. Default: false. |
| shareTargets | ShareTargets | No | Share the subnet with other accounts/OUs. |
| tags | Tag[] | No | Tags to apply to the subnet. |

### NatGateway

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the NAT gateway. |
| subnet | string | Yes | Subnet to place the NAT gateway in. |
| allocationId | string | No | Allocation ID of an Elastic IP to assign (bring your own EIP). |
| private | boolean | No | Create a private NAT gateway. Default: false. |
| tags | Tag[] | No | Tags to apply to the NAT gateway. |

### SecurityGroup

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the security group. |
| description | string | No | Description of the security group. |
| inboundRules | SecurityGroupRule[] | No | Inbound rules for the security group. |
| outboundRules | SecurityGroupRule[] | No | Outbound rules for the security group. |
| tags | Tag[] | No | Tags to apply to the security group. |

### SecurityGroupRule

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| description | string | No | Description of the security group rule. |
| ipProtocol | string | Yes | IP protocol for the rule. |
| fromPort | number | No | Starting port range for the rule. |
| toPort | number | No | Ending port range for the rule. |
| source | string[] | No | Source CIDR blocks or security group IDs. |

### VpcFlowLog

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| destinations | string[] | Yes | Log destinations: 'cloud-watch-logs', 's3'. |
| maxAggregationInterval | number | No | Maximum aggregation interval in seconds. Default: 600. |
| trafficType | string | No | Traffic to log: 'ALL', 'ACCEPT', 'REJECT'. Default: 'ALL'. |
| logFormat | string | No | Flow logs format specification. |
| tags | Tag[] | No | Tags to apply to flow log resources. |

### NetworkAcl

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the network ACL. |
| subnets | string[] | Yes | Subnets to associate with the NACL. |
| inboundRules | NetworkAclRule[] | No | Inbound rules for the NACL. |
| outboundRules | NetworkAclRule[] | No | Outbound rules for the NACL. |
| tags | Tag[] | No | Tags to apply to the NACL. |

### NetworkAclRule

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| rule | number | Yes | Rule number (1-32766). |
| protocol | number | Yes | Protocol number. |
| fromPort | number | No | Starting port range. |
| toPort | number | No | Ending port range. |
| action | string | Yes | 'allow' or 'deny'. |
| source | string | No | Source CIDR block. |

### GatewayEndpoint

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| defaultPolicy | string | No | Default policy for gateway endpoints. |
| endpoints | GatewayEndpointItem[] | Yes | Gateway endpoints to create. |

### GatewayEndpointItem

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| service | string | Yes | Service name: 's3' or 'dynamodb'. |
| policy | string | No | Custom policy for this endpoint. |
| routeTables | string[] | No | Route tables to create endpoint routes in. |

### InterfaceEndpoint

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| defaultPolicy | string | No | Default policy for interface endpoints. |
| central | boolean | No | Create as a central endpoint. Default: false. |
| subnets | string[] | Yes | Subnets to place the endpoints in. |
| segregateEndpoints | boolean | No | Place endpoints in separate security groups. Default: false. |
| includeS3Endpoints | boolean | No | Include S3 endpoint by default. Default: true. |
| endpoints | InterfaceEndpointItem[] | Yes | Interface endpoints to create. |

### InterfaceEndpointItem

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| service | string | Yes | AWS service name for the endpoint. |
| policy | string | No | Custom policy for this endpoint. |
| securityGroups | string[] | No | Security groups to associate with the endpoint. |

### TransitGatewayAttachment

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the attachment. |
| transitGateway | TransitGatewayReference | Yes | Transit gateway to attach to. |
| subnets | string[] | Yes | Subnets for the attachment. |
| routeTableAssociations | string[] | No | TGW route tables to associate the attachment with. |
| routeTablePropagations | string[] | No | TGW route tables to propagate routes to. |
| options | TransitGatewayAttachmentOptions | No | Additional attachment options. |

### TransitGatewayReference

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the transit gateway. |
| account | string | No | Account that owns the transit gateway (if not local). |

### TransitGatewayAttachmentOptions

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| applianceModeSupport | string | No | Enable appliance mode: 'enable' or 'disable'. |
| dnsSupport | string | No | Enable DNS support: 'enable' or 'disable'. |
| ipv6Support | string | No | Enable IPv6 support: 'enable' or 'disable'. |

### VirtualPrivateGateway

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| asn | number | Yes | ASN for the VGW. |
| vpnConnections | VpnConnection[] | No | VPN connections to create with this VGW. |

### VpnConnection

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the VPN connection. |
| customerGatewayId | string | Yes | Customer gateway ID to connect to. |
| routeTableAssociations | string[] | No | Route tables to associate with the connection. |
| tags | Tag[] | No | Tags to apply to the VPN connection. |

### VpcTemplate

Templates for creating multiple similar VPCs.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the template. |
| deploymentTargets | DeploymentTargets | Yes | Accounts/OUs to deploy templated VPCs to. |
| region | string | Yes | Region to deploy templated VPCs to. |
| cidrs | string[] | No | Static CIDR blocks for templated VPCs. |
| ipamAllocations | IpamAllocation[] | No | IPAM allocations for templated VPCs. |
| internetGateway | boolean | No | Create an internet gateway. Default: false. |
| enableDnsHostnames | boolean | No | Enable DNS hostnames. Default: true. |
| enableDnsSupport | boolean | No | Enable DNS support. Default: true. |
| instanceTenancy | string | No | Instance tenancy setting. Default: 'default'. |
| routeTables | RouteTable[] | No | Route tables for templated VPCs. |
| subnets | Subnet[] | No | Subnets for templated VPCs. |
| natGateways | NatGateway[] | No | NAT gateways for templated VPCs. |
| securityGroups | SecurityGroup[] | No | Security groups for templated VPCs. |
| transitGatewayAttachments | TransitGatewayAttachment[] | No | TGW attachments for templated VPCs. |
| tags | Tag[] | No | Tags to apply to templated VPCs. |

### IpamAllocation

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| ipamPoolName | string | Yes | Name of the IPAM pool to allocate from. |
| netmaskLength | number | Yes | Netmask length for the allocation. |
| tag | string | No | Key/value pair used to tag the IPAM allocation. |

### VpcFlowLogsConfig

Global VPC flow logs configuration.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| destinations | string[] | Yes | Log destinations: 'cloud-watch-logs', 's3'. |
| maxAggregationInterval | number | No | Maximum aggregation interval in seconds. Default: 600. |
| trafficType | string | No | Traffic to log: 'ALL', 'ACCEPT', 'REJECT'. Default: 'ALL'. |
| regions | string[] | No | Regions to enable flow logs in. |
| excludeRegions | string[] | No | Regions to exclude from flow logs. |
| vpcLookupOption | string | No | VPC lookup option: 'excludePrefixes' or 'includePrefixes'. |
| vpcLookupPrefixes | string[] | No | VPC Name prefixes to include/exclude. |
| deploymentTargets | DeploymentTargets | No | Specific targets to enable flow logs for. |
| excludeAccounts | string[] | No | Accounts to exclude from flow logs. |

### CentralNetworkServicesConfig

Configures centralized network services.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| delegatedAdminAccount | string | Yes | Account to use as delegated administrator. |
| ipams | Ipam[] | No | IPAM configurations. |
| route53Resolver | Route53ResolverConfig | No | Route 53 Resolver configuration. |
| networkFirewall | NetworkFirewallConfig | No | AWS Network Firewall configuration. |
| dnsFirewallRuleGroups | DnsFirewallRuleGroup[] | No | DNS Firewall rule groups. |

### Ipam

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the IPAM. |
| region | string | Yes | Region to create the IPAM in. |
| description | string | No | Description of the IPAM. |
| operatingRegions | string[] | Yes | Regions the IPAM will operate in. |
| pools | IpamPool[] | No | IPAM pools to create. |
| tags | Tag[] | No | Tags to apply to the IPAM. |

### IpamPool

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the IPAM pool. |
| description | string | No | Description of the IPAM pool. |
| provisionedCidrs | string[] | No | CIDRs to provision in the pool. |
| shareTargets | ShareTargets | No | Share the pool with other accounts/OUs. |
| locale | string | No | Locale for the pool (AWS Region). |
| sourceIpamPool | string | No | Source IPAM pool to draw from. |
| tags | Tag[] | No | Tags to apply to the IPAM pool. |

### Route53ResolverConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| endpoints | ResolverEndpoint[] | No | Route 53 Resolver endpoints. |
| queryLogs | ResolverQueryLogs | No | Route 53 Resolver query logs configuration. |
| firewallRuleGroups | ResolverFirewallRuleGroup[] | No | Route 53 Resolver firewall rule groups. |

### ResolverEndpoint

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the Resolver endpoint. |
| type | string | Yes | Type of endpoint: 'INBOUND' or 'OUTBOUND'. |
| vpc | string | Yes | VPC to create the endpoint in. |
| subnets | string[] | Yes | Subnets to place the endpoint in. |
| allowedCidrs | string[] | No | CIDRs allowed to use the endpoint (for INBOUND) |
| rules | ResolverRule[] | No | Resolver rules to associate (for OUTBOUND). |
| tags | Tag[] | No | Tags to apply to the endpoint. |

### ResolverRule

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the Resolver rule. |
| domainName | string | Yes | Domain name for the rule. |
| targetIps | TargetIp[] | Yes | Target IPs for DNS resolution. |
| ruleType | string | No | Type of rule: 'FORWARD' or 'SYSTEM'. Default: 'FORWARD'. |
| shareTargets | ShareTargets | No | Share the rule with other accounts/OUs. |
| tags | Tag[] | No | Tags to apply to the rule. |

### TargetIp

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| ip | string | Yes | IP address to forward queries to. |
| port | string | No | Port to forward queries to. Default: '53'. |

### ResolverQueryLogs

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the query logging configuration. |
| destinations | string[] | Yes | Log destinations: 's3' or 'cloud-watch-logs'. |
| shareTargets | ShareTargets | No | Share the configuration with other accounts/OUs. |

### ResolverFirewallRuleGroup

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the firewall rule group. |
| regions | string[] | Yes | Regions to deploy the rule group to. |
| rules | ResolverFirewallRule[] | Yes | Rules within the group. |
| shareTargets | ShareTargets | No | Share the rule group with other accounts/OUs. |
| tags | Tag[] | No | Tags to apply to the rule group. |

### ResolverFirewallRule

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the firewall rule. |
| action | string | Yes | Action: 'ALLOW', 'BLOCK', or 'ALERT'. |
| priority | number | Yes | Priority of the rule (0-99). |
| blockResponse | string | No | Response for blocked queries: 'NODATA', 'NXDOMAIN', or 'OVERRIDE'. |
| blockOverrideTtl | number | No | TTL for override responses. |
| blockOverrideDomain | string | No | Domain for override responses. |
| domainLists | string[] | No | Domain lists to apply the rule to. |
| managedDomainList | string | No | Managed domain list to apply the rule to. |

### NetworkFirewallConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| enable | boolean | Yes | Whether to enable Network Firewall. |
| firewalls | NetworkFirewall[] | No | Network Firewalls to deploy. |
| policies | NetworkFirewallPolicy[] | No | Network Firewall policies to create. |
| ruleGroups | NetworkFirewallRuleGroup[] | No | Network Firewall rule groups to create. |

### NetworkFirewall

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the firewall. |
| firewallPolicy | string | Yes | Name of the firewall policy to use. |
| vpc | string | Yes | VPC to deploy the firewall to. |
| subnets | string[] | Yes | Subnets to place the firewall in. |
| loggingConfiguration | NetworkFirewallLogging | No | Logging configuration for the firewall. |
| description | string | No | Description of the firewall. |
| deleteProtection | boolean | No | Enable deletion protection. Default: false. |
| tags | Tag[] | No | Tags to apply to the firewall. |

### NetworkFirewallPolicy

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the firewall policy. |
| description | string | No | Description of the policy. |
| regions | string[] | Yes | Regions to deploy the policy to. |
| shareTargets | ShareTargets | No | Share the policy with other accounts/OUs. |
| firewallPolicy | NetworkFirewallPolicyDefinition | Yes | Definition of the firewall policy. |
| tags | Tag[] | No | Tags to apply to the policy. |

### NetworkFirewallPolicyDefinition

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| statelessDefaultActions | string[] | Yes | Default actions for stateless rules. |
| statelessFragmentDefaultActions | string[] | Yes | Default actions for stateless fragments. |
| statelessRuleGroups | StatelessRuleGroupReference[] | No | Stateless rule group references. |
| statefulRuleGroups | StatefulRuleGroupReference[] | No | Stateful rule group references. |
| statefulDefaultActions | string[] | No | Default actions for stateful rules. |

### TransitGateway

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the transit gateway. |
| account | string | Yes | Account to create the transit gateway in. |
| region | string | Yes | Region to deploy the transit gateway to. |
| shareTargets | ShareTargets | No | Share the transit gateway with other accounts/OUs. |
| asn | number | Yes | ASN for the transit gateway. |
| dnsSupport | string | No | Enable DNS support: 'enable' or 'disable'. Default: 'enable'. |
| vpnEcmpSupport | string | No | Enable VPN ECMP support: 'enable' or 'disable'. Default: 'enable'. |
| defaultRouteTableAssociation | string | No | Default route table association: 'enable' or 'disable'. Default: 'disable'. |
| defaultRouteTablePropagation | string | No | Default route table propagation: 'enable' or 'disable'. Default: 'disable'. |
| autoAcceptSharingAttachments | string | No | Auto-accept shared attachments: 'enable' or 'disable'. Default: 'disable'. |
| routeTables | TransitGatewayRouteTable[] | Yes | Route tables for the transit gateway. |
| tags | Tag[] | No | Tags to apply to the transit gateway. |

### TransitGatewayRouteTable

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the route table. |
| routes | TransitGatewayRoute[] | No | Routes in the route table. |
| tags | Tag[] | No | Tags to apply to the route table. |

### TransitGatewayRoute

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| destinationCidrBlock | string | Yes | Destination CIDR block for the route. |
| attachment | TransitGatewayRouteAttachment | Yes | Attachment for the route. |
| blackhole | boolean | No | Create as a blackhole route. Default: false. |

### TransitGatewayRouteAttachment

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the attachment. |
| account | string | No | Account that owns the attachment (if not local). |
| region | string | No | Region where the attachment exists (if cross-region). |

### EndpointPolicy

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the policy. |
| document | string | Yes | Path to the policy document JSON file. |
| tags | Tag[] | No | Tags to apply to the policy. |

### DeploymentTargets

Defines the targets for resource deployment.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| organizationalUnits | string[] | No | OUs to deploy resources to. |
| accounts | string[] | No | Specific accounts to deploy resources to. |
| excludedAccounts | string[] | No | Accounts to exclude from deployment. |
| excludedRegions | string[] | No | Regions to exclude from deployment. |

### ShareTargets

Targets for resource sharing via AWS RAM.

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| organizationalUnits | string[] | No | OUs to share resources with. |
| accounts | string[] | No | Specific accounts to share resources with. |

---

## organization-config.yaml

This file defines the AWS Organizations structure and organizational policies.

### Schema

```yaml
# Root level properties
enable: boolean
organizationalUnits: OrganizationalUnit[]
serviceControlPolicies: ServiceControlPolicy[]
taggingPolicies: TaggingPolicy[]
backupPolicies: BackupPolicy[]
quarantineNewAccounts: QuarantineNewAccountsConfig
chatbotPolicies: ChatbotPolicy[]
```

### OrganizationalUnit

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the organizational unit. |
| enable | boolean | No | Enable creating this OU. Default: true. |
| childOUs | OrganizationalUnit[] | No | Child organizational units. |

### ServiceControlPolicy

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the SCP. |
| description | string | No | Description of the policy. |
| policy | string | Yes | Path to the policy JSON file or inline JSON. |
| type | string | Yes | Type of policy: 'awsManaged' or 'customerManaged'. |
| deploymentTargets | DeploymentTargets | No | Accounts/OUs to attach the policy to. |
| tags | Tag[] | No | Tags to apply to the policy. |

### TaggingPolicy

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the tagging policy. |
| description | string | No | Description of the policy. |
| policy | string | Yes | Path to the policy JSON file or inline JSON. |
| deploymentTargets | DeploymentTargets | No | Accounts/OUs to attach the policy to. |
| tags | Tag[] | No | Tags to apply to the policy. |

### BackupPolicy

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the backup policy. |
| description | string | No | Description of the policy. |
| policy | string | Yes | Path to the policy JSON file or inline JSON. |
| deploymentTargets | DeploymentTargets | No | Accounts/OUs to attach the policy to. |
| tags | Tag[] | No | Tags to apply to the policy. |

### QuarantineNewAccountsConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| enable | boolean | Yes | Enable quarantine policy for new accounts. |
| scpPolicyName | string | No | Name of the SCP to apply to quarantined accounts. |
| tagPolicyName | string | No | Name of the tag policy to apply to quarantined accounts. |
| backupPolicyName | string | No | Name of the backup policy to apply to quarantined accounts. |

### ChatbotPolicy

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the Chatbot policy. |
| description | string | No | Description of the policy. |
| policy | string | Yes | Path to the policy JSON file or inline JSON. |
| deploymentTargets | DeploymentTargets | No | Accounts/OUs to attach the policy to. |
| tags | Tag[] | No | Tags to apply to the policy. |

---

## security-config.yaml

This file defines security services and configurations.

### Schema

```yaml
# Root level properties
centralSecurityServices: CentralSecurityServicesConfig
accessAnalyzer: AccessAnalyzerConfig
iamPasswordPolicy: IamPasswordPolicyConfig
awsConfig: AwsConfig
cloudWatch: CloudWatchConfig
keyManagementService: KeyManagementServiceConfig
```

### CentralSecurityServicesConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| delegatedAdminAccount | string | Yes | Account to use as security delegated administrator. |
| ebsDefaultVolumeEncryption | EbsEncryptionConfig | No | EBS default encryption configuration. |
| s3PublicAccessBlock | S3PublicAccessBlockConfig | No | S3 public access block configuration. |
| snsTopicName | string | No | SNS topic for security notifications. |
| guardduty | GuardDutyConfig | No | GuardDuty configuration. |
| securityHub | SecurityHubConfig | No | Security Hub configuration. |
| macie | MacieConfig | No | Macie configuration. |
| auditManager | AuditManagerConfig | No | Audit Manager configuration. |
| detective | DetectiveConfig | No | Detective configuration. |
| ssmAutomation | SsmAutomationConfig | No | SSM Automation configuration. |
| scpRevertChangesConfig | ScpRevertChangesConfig | No | Configuration for reverting SCP changes. |

### EbsEncryptionConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| enable | boolean | Yes | Enable EBS default encryption. |
| kmsKey | string | No | KMS key ID for encryption. |
| excludeRegions | string[] | No | Regions to exclude from EBS encryption. |

### S3PublicAccessBlockConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| enable | boolean | Yes | Enable S3 public access block. |
| excludeAccounts | string[] | No | Accounts to exclude from S3 public access block. |

### GuardDutyConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| enable | boolean | Yes | Enable GuardDuty. |
| excludeRegions | string[] | No | Regions to exclude from GuardDuty. |
| s3Protection | GuardDutyS3ProtectionConfig | No | S3 protection configuration. |
| exportConfiguration | GuardDutyExportConfig | No | Export configuration for findings. |
| ecrProtection | GuardDutyEcrProtectionConfig | No | ECR protection configuration. |
| eksProtection | GuardDutyEksProtectionConfig | No | EKS protection configuration. |
| lambdaProtection | GuardDutyLambdaProtectionConfig | No | Lambda protection configuration. |
| malwareProtection | GuardDutyMalwareProtectionConfig | No | Malware protection configuration. |

### GuardDutyS3ProtectionConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| enable | boolean | Yes | Enable S3 protection. |
| excludeRegions | string[] | No | Regions to exclude from S3 protection. |

### GuardDutyExportConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| enable | boolean | Yes | Enable findings export. |
| overrideExisting | boolean | No | Override existing export configuration. Default: false. |
| destinationType | string | Yes | Destination type: 'S3'. |
| exportFrequency | string | Yes | Export frequency: 'FIFTEEN_MINUTES', 'ONE_HOUR', or 'SIX_HOURS'. |

### SecurityHubConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| enable | boolean | Yes | Enable Security Hub. |
| regionAggregation | boolean | No | Enable region aggregation. Default: true. |
| excludeRegions | string[] | No | Regions to exclude from Security Hub. |
| standards | SecurityHubStandard[] | No | Security standards to enable. |
| securityControlsConfiguration | SecurityControlsConfiguration | No | Security controls configuration. |
| snsTopicName | string | No | SNS topic for notifications. |
| notificationLevel | string | No | Level for notifications: 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', or 'INFORMATIONAL'. |

### SecurityHubStandard

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the security standard. |
| enable | boolean | Yes | Enable this standard. |
| controlsToDisable | string[] | No | Controls to disable within this standard. |

### SecurityControlsConfiguration

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| disabledSecurityControls | DisabledSecurityControl[] | No | Security controls to disable globally. |
| parametersToUpdate | SecurityControlParameter[] | No | Parameters to update for security controls. |

### DisabledSecurityControl

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| controlIdentifier | string | Yes | Identifier of the security control. |
| reason | string | Yes | Reason for disabling: 'NOT_APPLICABLE', 'SECURITY_CONTROL_INEFFECTIVE', etc. |
| standardsToDisableOnly | string[] | No | Only disable this control in specific standards. |

### SecurityControlParameter

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| controlIdentifier | string | Yes | Identifier of the security control. |
| parameters | object | Yes | Parameter values to update. |
| standardsToUpdateOnly | string[] | No | Only update parameters in specific standards. |

### MacieConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| enable | boolean | Yes | Enable Macie. |
| excludeRegions | string[] | No | Regions to exclude from Macie. |
| policyFindingsPublishingFrequency | string | No | Frequency for publishing policy findings. |
| publishSensitiveDataFindings | boolean | No | Publish sensitive data findings to Security Hub. Default: true. |

### AuditManagerConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| enable | boolean | Yes | Enable Audit Manager. |
| excludeRegions | string[] | No | Regions to exclude from Audit Manager. |
| defaultReportsConfiguration | AuditManagerDefaultReportsConfig | No | Default reports configuration. |
| lifecycleRules | LifecycleRule[] | No | Lifecycle rules for report storage. |

### AuditManagerDefaultReportsConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| enable | boolean | Yes | Enable default reports configuration. |
| destinationType | string | Yes | Destination type: 'S3'. |

### DetectiveConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| enable | boolean | Yes | Enable Detective. |
| excludeRegions | string[] | No | Regions to exclude from Detective. |

### SsmAutomationConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| excludeRegions | string[] | No | Regions to exclude from SSM Automation. |
| documentSets | SsmDocumentSet[] | No | SSM document sets to deploy. |

### SsmDocumentSet

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| shareTargets | ShareTargets | Yes | Targets to share documents with. |
| documents | SsmDocument[] | Yes | SSM documents to deploy. |

### SsmDocument

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the SSM document. |
| template | string | Yes | Path to the document template. |
| type | string | No | Type of document. Default: 'Automation'. |
| tags | Tag[] | No | Tags to apply to the document. |

### ScpRevertChangesConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| enable | boolean | Yes | Enable automatic reverting of SCP changes. |
| snsTopicName | string | No | SNS topic for SCP change notifications. |

### AccessAnalyzerConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| enable | boolean | Yes | Enable Access Analyzer. |
| excludeRegions | string[] | No | Regions to exclude from Access Analyzer. |

### IamPasswordPolicyConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| allowUsersToChangePassword | boolean | No | Allow users to change their password. Default: true. |
| hardExpiry | boolean | No | Prevent password reuse after expiration. Default: false. |
| requireUppercaseCharacters | boolean | No | Require uppercase characters. Default: true. |
| requireLowercaseCharacters | boolean | No | Require lowercase characters. Default: true. |
| requireSymbols | boolean | No | Require symbols. Default: true. |
| requireNumbers | boolean | No | Require numbers. Default: true. |
| minimumPasswordLength | number | No | Minimum password length. Default: 14. |
| passwordReusePrevention | number | No | Number of previous passwords to prevent reuse. Default: 24. |
| maxPasswordAge | number | No | Maximum password age in days. Default: 90. |

### AwsConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| enableConfigurationRecorder | boolean | No | Enable AWS Config configuration recorder. Default: true. |
| enableDeliveryChannel | boolean | No | Enable AWS Config delivery channel. Default: true. |
| ruleSets | ConfigRuleSet[] | No | AWS Config rule sets to deploy. |

### ConfigRuleSet

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| deploymentTargets | DeploymentTargets | Yes | Targets to deploy the rule set to. |
| rules | ConfigRule[] | Yes | AWS Config rules to deploy. |
| remediations | ConfigRemediation[] | No | AWS Config remediations to deploy. |

### ConfigRule

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the Config rule. |
| description | string | No | Description of the rule. |
| identifier | string | Yes | AWS Config managed rule identifier or 'Custom' for custom rules. |
| inputParameters | object | No | Input parameters for the rule. |
| complianceResourceTypes | string[] | No | Resource types to evaluate. |
| tags | Tag[] | No | Tags to apply to the rule. |

### ConfigRemediation

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the remediation. |
| configRuleName | string | Yes | Config rule to remediate. |
| targetId | string | Yes | SSM document or automation ARN to use for remediation. |
| parameters | object | No | Parameters for the remediation. |
| retryAttemptSeconds | number | No | Seconds to wait before retry. Default: 60. |
| maximumAutomaticAttempts | number | No | Maximum automatic retry attempts. Default: 5. |
| executionControls | ExecutionControls | No | Execution controls for remediation. |

### ExecutionControls

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| ssmControls | SsmControls | No | SSM controls for execution. |

### SsmControls

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| concurrentExecutionRatePercentage | number | No | Percentage of concurrency for execution. |
| errorPercentage | number | No | Percentage of errors allowed. |

### CloudWatchConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| metricSets | MetricSet[] | No | CloudWatch metric sets to create. |
| alarmSets | AlarmSet[] | No | CloudWatch alarm sets to create. |
| logSets | LogSet[] | No | Log sets to create. |

### MetricSet

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| deploymentTargets | DeploymentTargets | Yes | Targets to deploy metrics to. |
| regions | string[] | No | Regions to deploy metrics to. |
| metrics | Metric[] | Yes | CloudWatch metrics to create. |

### Metric

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the metric. |
| namespace | string | Yes | Namespace for the metric. |
| dimensions | MetricDimension[] | No | Dimensions for the metric. |
| filter | LogFilter | No | Log filter pattern for metric. |
| filterName | string | No | Name of the metric filter. |
| logGroupName | string | No | Log group to filter from. |
| treatMissingData | string | No | How to treat missing data: 'notBreaching', 'breaching', 'ignore', 'missing'. |
| unit | string | No | Unit for the metric. |

### MetricDimension

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the dimension. |
| value | string | Yes | Value of the dimension. |

### LogFilter

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| pattern | string | Yes | Filter pattern for logs. |
| defaultValue | number | No | Default value when pattern doesn't match. |

### AlarmSet

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| deploymentTargets | DeploymentTargets | Yes | Targets to deploy alarms to. |
| regions | string[] | No | Regions to deploy alarms to. |
| alarms | Alarm[] | Yes | CloudWatch alarms to create. |

### Alarm

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the alarm. |
| description | string | No | Description of the alarm. |
| namespace | string | Yes | Namespace for the metric. |
| metricName | string | Yes | Name of the metric to alarm on. |
| threshold | number | Yes | Threshold for the alarm. |
| statistic | string | No | Statistic to use: 'Average', 'Maximum', 'Minimum', 'SampleCount', or 'Sum'. Default: 'Average'. |
| comparisonOperator | string | No | Comparison operator for the alarm. |
| evaluationPeriods | number | No | Number of periods to evaluate. Default: 1. |
| period | number | No | Period in seconds. Default: 300. |
| treatMissingData | string | No | How to treat missing data: 'notBreaching', 'breaching', 'ignore', 'missing'. |
| dimensions | MetricDimension[] | No | Dimensions for the metric. |
| alarmActions | string[] | No | SNS topics or other actions to trigger on alarm. |
| tags | Tag[] | No | Tags to apply to the alarm. |

### KeyManagementServiceConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| keySets | KeySet[] | No | KMS key sets to create. |

### KeySet

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| deploymentTargets | DeploymentTargets | Yes | Targets to deploy keys to. |
| regions | string[] | No | Regions to deploy keys to. |
| keys | Key[] | Yes | KMS keys to create. |

### Key

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the key. |
| description | string | No | Description of the key. |
| enabled | boolean | No | Whether the key is enabled. Default: true. |
| enableKeyRotation | boolean | No | Enable automatic key rotation. Default: true. |
| policy | string | No | Key policy document or path to policy file. |
| alias | string | No | Alias for the key. |
| tags | Tag[] | No | Tags to apply to the key. |

---

## customizations-config.yaml

This file defines additional customizations including CloudFormation templates, Service Catalog, and various AWS resources.

### Schema

```yaml
# Root level properties
customizations:
  cloudFormationTemplates: CloudFormationTemplate[]
  cloudFormationStackSets: CloudFormationStackSet[]
  serviceCatalogPortfolios: ServiceCatalogPortfolio[]
  applications: Application[]
  parameters: Parameter[]
  ssmParameters: SsmParameter[]
  snsTopics: SnsTopicConfig
  ssmInventory: SsmInventoryConfig
  scpPolicies: ServiceControlPolicy[]
```

### CloudFormationTemplate

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the CloudFormation template. |
| description | string | No | Description of the template. |
| template | string | Yes | Path to the CloudFormation template file. |
| parameters | TemplateParameter[] | No | Parameters for the template. |
| deploymentTargets | DeploymentTargets | Yes | Targets to deploy the template to. |
| regions | string[] | No | Regions to deploy the template to. |
| terminationProtection | boolean | No | Enable termination protection. Default: false. |
| depends | string[] | No | Templates this template depends on. |
| capabilities | string[] | No | CloudFormation capabilities required. |
| tags | Tag[] | No | Tags to apply to the stack. |

### TemplateParameter

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the parameter. |
| value | string | Yes | Value for the parameter. |

### CloudFormationStackSet

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the StackSet. |
| description | string | No | Description of the StackSet. |
| template | string | Yes | Path to the CloudFormation template file. |
| parameters | TemplateParameter[] | No | Parameters for the StackSet. |
| deploymentTargets | DeploymentTargets | Yes | Targets to deploy the StackSet to. |
| regions | string[] | Yes | Regions to deploy the StackSet to. |
| concurrencyMode | string | No | Concurrency mode: 'SEQUENTIAL' or 'PARALLEL'. Default: 'PARALLEL'. |
| maxConcurrentPercentage | number | No | Maximum concurrent percentage. Default: 100. |
| failureTolerancePercentage | number | No | Failure tolerance percentage. Default: 0. |
| capabilities | string[] | No | CloudFormation capabilities required. |
| tags | Tag[] | No | Tags to apply to the StackSet. |

### ServiceCatalogPortfolio

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the portfolio. |
| description | string | No | Description of the portfolio. |
| provider | string | Yes | Provider of the portfolio. |
| account | string | No | Account to create the portfolio in. |
| shareTargets | ShareTargets | No | Targets to share the portfolio with. |
| shareTagOptions | boolean | No | Share tag options. Default: false. |
| products | ServiceCatalogProduct[] | No | Products to add to the portfolio. |
| tagOptions | TagOption[] | No | Tag options for the portfolio. |

### ServiceCatalogProduct

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the product. |
| description | string | No | Description of the product. |
| owner | string | Yes | Owner of the product. |
| templatePath | string | Yes | Path to the product template. |
| deploymentTargets | DeploymentTargets | No | Targets to deploy the product to. |
| tagOptions | TagOption[] | No | Tag options for the product. |
| tags | Tag[] | No | Tags to apply to the product. |

### TagOption

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| key | string | Yes | Key for the tag option. |
| values | string[] | Yes | Allowed values for the tag option. |

### Application

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the application. |
| description | string | No | Description of the application. |
| account | string | Yes | Account to deploy the application to. |
| region | string | Yes | Region to deploy the application to. |
| resourceGroups | ResourceGroup[] | No | Resource groups for the application. |
| stacks | CloudFormationTemplate[] | No | CloudFormation stacks for the application. |
| tags | Tag[] | No | Tags to apply to the application. |

### ResourceGroup

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the resource group. |
| filters | ResourceFilter[] | No | Filters for resources in the group. |
| queries | ResourceQuery[] | No | Queries for resources in the group. |
| tags | Tag[] | No | Tags to apply to the resource group. |

### ResourceFilter

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| type | string | Yes | Type of filter: 'TAG', 'RESOURCE_TYPE', etc. |
| key | string | Yes | Key for the filter. |
| values | string[] | Yes | Values for the filter. |

### ResourceQuery

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| query | string | Yes | Query string in CloudFormation syntax. |
| type | string | Yes | Query type: 'TAG_FILTERS_1_0', 'CLOUDFORMATION_STACK_1_0'. |

### Parameter

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the SSM parameter. |
| value | string | Yes | Value for the parameter. |
| type | string | No | Parameter type: 'String', 'StringList', 'SecureString'. Default: 'String'. |
| deploymentTargets | DeploymentTargets | Yes | Targets to deploy the parameter to. |
| regions | string[] | No | Regions to deploy the parameter to. |
| tags | Tag[] | No | Tags to apply to the parameter. |

### SsmParameter

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| name | string | Yes | Name of the SSM parameter. |
| value | string | Yes | Value for the parameter. |
| type | string | No | Parameter type: 'String', 'StringList', 'SecureString'. Default: 'String'. |
| deploymentTargets | DeploymentTargets | Yes | Targets to deploy the parameter to. |
| regions | string[] | No | Regions to deploy the parameter to. |
| tags | Tag[] | No | Tags to apply to the parameter. |

### SsmInventoryConfig

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| enable | boolean | Yes | Enable SSM Inventory. |
| deploymentTargets | DeploymentTargets | No | Targets to deploy inventory to. |
| regions | string[] | No | Regions to enable inventory in. |
| excludeRegions | string[] | No | Regions to exclude from inventory. |
| excludeAccounts | string[] | No | Accounts to exclude from inventory. |
| scheduleExpression | string | No | Schedule for inventory collection. Default: 'rate(1 day)'. |

---

## Common Types

### LifecycleRule

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| enabled | boolean | Yes | Whether the rule is enabled. |
| id | string | No | Identifier for the rule. |
| abortIncompleteMultipartUpload | number | No | Days after which to abort incomplete multipart uploads. |
| expiration | number | No | Days after which to expire objects. |
| expiredObjectDeleteMarker | boolean | No | Remove expired delete markers. |
| noncurrentVersionExpiration | number | No | Days after which to expire noncurrent versions. |
| noncurrentVersionTransitions | LifecycleTransition[] | No | Transitions for noncurrent versions. |
| transitions | LifecycleTransition[] | No | Transitions for current versions. |

### LifecycleTransition

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| storageClass | string | Yes | Storage class to transition to. |
| transitionAfter | number | Yes | Days after which to transition objects. |

### Tag

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| key | string | Yes | Tag key. |
| value | string | Yes | Tag value. |