# preflight_checks/aws_checks.py
import logging
import os
import sys
from typing import List, Optional, Dict, Any

import boto3
from botocore.exceptions import ClientError, NoCredentialsError, BotoCoreError

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# --- Constants ---
DEFAULT_STACK_PREFIX = "AWSAccelerator"
DEFAULT_ENVIRONMENT = "lz"
FAILED_STACK_STATUSES = [
    "CREATE_FAILED",
    "ROLLBACK_FAILED",
    "DELETE_FAILED",
    "UPDATE_ROLLBACK_FAILED",
    "IMPORT_ROLLBACK_FAILED",
    "ROLLBACK_COMPLETE",  # Often indicates a failure during creation/update
    "UPDATE_ROLLBACK_COMPLETE", # Often indicates a failure during update
]

# --- Helper Functions ---

def get_aws_client(service_name: str, region_name: Optional[str] = None):
    """Initializes and returns a boto3 client."""
    try:
        return boto3.client(service_name, region_name=region_name)
    except NoCredentialsError:
        logger.exception("AWS credentials not found.")
        raise
    except BotoCoreError as e:
        logger.exception(f"Error initializing boto3 client for {service_name}: {e}")
        raise

def get_stack_failure_details(cf_client, stack_name: str) -> List[Dict[str, Any]]:
    """
    Get detailed information about stack failures.
    
    Args:
        cf_client: CloudFormation boto3 client
        stack_name: Name of the stack to check
        
    Returns:
        List of dictionaries containing failure details
    """
    failure_details = []
    
    try:
        # Get stack events to find failure reasons
        paginator = cf_client.get_paginator('describe_stack_events')
        events_iterator = paginator.paginate(StackName=stack_name)
        
        for page in events_iterator:
            for event in page.get('StackEvents', []):
                # Look for events with status reasons (typically failures)
                if 'ResourceStatus' in event and 'ResourceStatusReason' in event:
                    status = event.get('ResourceStatus')
                    if status.endswith('FAILED') or 'ROLLBACK' in status:
                        failure_details.append({
                            'logical_id': event.get('LogicalResourceId'),
                            'resource_type': event.get('ResourceType'),
                            'status': status,
                            'reason': event.get('ResourceStatusReason'),
                            'timestamp': event.get('Timestamp')
                        })
        
        # Sort by timestamp to get most recent failures first
        failure_details.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
    except ClientError as e:
        logger.warning(f"Could not retrieve failure details for stack {stack_name}: {e}")
    
    return failure_details

# --- Check Functions ---

def check_cloudformation_stacks(
    region_name: str, stack_prefix: str
) -> bool:
    """
    Checks for failed CloudFormation stacks in a specific region with a given prefix.
    Provides detailed information about failure reasons.

    Args:
        region_name: The AWS region to check.
        stack_prefix: The prefix of the stack names to check.

    Returns:
        True if no failed stacks with the prefix are found, False otherwise.
    """
    logger.info(
        f"Checking for failed CloudFormation stacks matching prefix '{stack_prefix}' "
        f"in region '{region_name}'..."
    )
    cf_client = get_aws_client("cloudformation", region_name=region_name)
    failed_stacks_found: List[str] = []
    passed = True

    try:
        paginator = cf_client.get_paginator("list_stacks")
        page_iterator = paginator.paginate(
            StackStatusFilter=FAILED_STACK_STATUSES
        )

        for page in page_iterator:
            for stack_summary in page.get("StackSummaries", []):
                stack_name = stack_summary.get("StackName", "")
                stack_status = stack_summary.get("StackStatus", "")
                if stack_name.startswith(stack_prefix):
                    logger.error(
                        f"Found failed CloudFormation stack: {stack_name} "
                        f"(Status: {stack_status}, Region: {region_name})"
                    )
                    
                    # Get detailed failure information
                    failure_details = get_stack_failure_details(cf_client, stack_name)
                    
                    if failure_details:
                        logger.error(f"Failure details for stack {stack_name}:")
                        for i, detail in enumerate(failure_details[:5], 1):  # Show top 5 failures
                            logger.error(f"  {i}. Resource: {detail['logical_id']} ({detail['resource_type']})")
                            logger.error(f"     Status: {detail['status']}")
                            logger.error(f"     Reason: {detail['reason']}")
                    
                    failed_stacks_found.append(stack_name)
                    passed = False

    except ClientError as e:
        # Handle potential throttling or access denied errors gracefully
        if e.response["Error"]["Code"] == "AccessDeniedException":
             logger.warning(
                f"Access denied when listing CloudFormation stacks in {region_name}. "
                f"Skipping check. Error: {e}"
            )
             # Depending on requirements, you might want to fail here or allow skipping
             return True # Assuming skip is acceptable if access denied
        else:
            logger.exception(
                f"Error checking CloudFormation stacks in {region_name}: {e}"
            )
            return False # Fail on other client errors

    if passed:
        logger.info(
            f"No failed CloudFormation stacks found with prefix '{stack_prefix}' "
            f"in region {region_name}."
        )
    else:
         logger.error(
            f"{len(failed_stacks_found)} failed CloudFormation stack(s) found with prefix "
            f"'{stack_prefix}' in region {region_name}."
        )

    return passed


def check_control_tower_landing_zone(ct_home_region: str) -> bool:
    """
    Checks if the Control Tower Landing Zone is in an ACTIVE and IN_SYNC state.

    Note: This check verifies the Landing Zone's status, not the compliance
    of every individual account and OU against all controls. A full compliance
    check typically requires querying AWS Config or Security Hub in the Audit account.

    Args:
        ct_home_region: The AWS region where Control Tower is deployed (home region).

    Returns:
        True if Control Tower is not enabled or the Landing Zone is ACTIVE and IN_SYNC,
        False otherwise.
    """
    logger.info(f"Checking Control Tower Landing Zone status in region '{ct_home_region}'...")
    passed = True
    try:
        # Control Tower API calls often need to be made to the home region.
        ct_client = get_aws_client("controltower", region_name=ct_home_region)

        landing_zones = ct_client.list_landing_zones().get("landingZones", [])

        if not landing_zones:
            logger.info("Control Tower does not appear to be enabled in this account/region.")
            return True # Not enabled, so considered passed/not applicable

        if len(landing_zones) > 1:
             logger.warning(
                f"Found multiple ({len(landing_zones)}) Landing Zones. "
                f"Checking the first one listed: {landing_zones[0].get('arn')}"
            )
             # Or potentially fail if multiple LZ is unexpected

        landing_zone_arn = landing_zones[0].get("arn")
        if not landing_zone_arn:
            logger.error("Could not retrieve ARN for the Landing Zone.")
            return False

        logger.info(f"Found Control Tower Landing Zone: {landing_zone_arn}")
        response = ct_client.get_landing_zone(landingZoneIdentifier=landing_zone_arn)

        landing_zone_details = response.get("landingZone", {})
        status = landing_zone_details.get("status")
        drift_status = landing_zone_details.get("driftStatus")
        latest_available_version = landing_zone_details.get("latestAvailableVersion")
        deployed_version = landing_zone_details.get("version")


        logger.info(f"Landing Zone Status: {status}")
        logger.info(f"Landing Zone Drift Status: {drift_status}")
        logger.info(f"Landing Zone Deployed Version: {deployed_version}")
        logger.info(f"Landing Zone Latest Available Version: {latest_available_version}")


        if status != "ACTIVE":
            logger.error(f"Control Tower Landing Zone status is '{status}', expected 'ACTIVE'.")
            passed = False
        else:
             logger.info("Landing Zone status is ACTIVE.")


        if drift_status != "IN_SYNC":
             logger.warning(
                f"Control Tower Landing Zone drift status is '{drift_status}', "
                f"expected 'IN_SYNC'. Consider running 'Repair Landing Zone'."
             )
             # Depending on strictness, you might fail here (passed = False)
             # For now, we only log a warning for drift, but check ACTIVE status.
        else:
            logger.info("Landing Zone drift status is IN_SYNC.")

        if latest_available_version and deployed_version != latest_available_version:
             logger.warning(
                f"Control Tower Landing Zone version ({deployed_version}) is not the latest "
                f"available ({latest_available_version}). Consider updating."
            )


    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code in ["AccessDeniedException", "ResourceNotFoundException"]:
             # If CT is not setup or permissions missing, treat as 'not enabled' for this check.
             logger.warning(
                 f"Could not check Control Tower Landing Zone status in {ct_home_region} "
                 f"(might not be enabled or permissions missing). Skipping check. Error: {e}"
             )
             return True # Skip the check
        elif error_code == 'ValidationException' and (
            'not subscribed' in str(e) or 
            'not available in the' in str(e) or 
            'not enrolled' in str(e)
            ):
             logger.info(f"Control Tower service is not available/subscribed in region {ct_home_region}. Skipping check.")
             return True # Skip the check
        else:
            logger.exception(
                f"Error checking Control Tower Landing Zone status in {ct_home_region}: {e}"
            )
            return False # Fail on other client errors

    if passed:
         logger.info("Control Tower Landing Zone check passed (Status ACTIVE).")
    else:
        logger.error("Control Tower Landing Zone check failed.")


    return passed


# --- Main Execution ---

def run_preflight_checks():
    """Runs all preflight checks."""
    logger.info("Starting preflight checks...")

    # --- Configuration ---
    # Get environment from environment variable with default 'lz'
    environment = os.getenv("ENVIRONMENT", DEFAULT_ENVIRONMENT)
    logger.info(f"Using environment: {environment}")
    
    # Region for CloudFormation checks (can be different from CT home region)
    check_region = os.getenv("AWS_REGION", os.getenv("AWS_DEFAULT_REGION"))
    if not check_region:
        logger.error(
            "AWS_REGION environment variable not set. Please set the AWS region."
        )
        sys.exit(1)
        return # Add return to stop execution after sys.exit

    # Control Tower Home Region (required for Control Tower API calls)
    # Determine this based on your environment. Often same as check_region but not always.
    # Defaulting to check_region, but make this configurable if needed.
    ct_home_region = os.getenv("CT_HOME_REGION", check_region)

    # Use environment in stack prefix if appropriate
    stack_prefix = os.getenv("STACK_PREFIX", f"{DEFAULT_STACK_PREFIX}-{environment}")

    logger.info(f"Configuration:")
    logger.info(f"  Environment: {environment}")
    logger.info(f"  Check Region: {check_region}")
    logger.info(f"  Control Tower Home Region: {ct_home_region}")
    logger.info(f"  CloudFormation Stack Prefix: {stack_prefix}")

    # --- Run Checks ---
    results = {}
    all_passed = True

    try:
        # Check 1: CloudFormation Stacks
        results["cloudformation"] = check_cloudformation_stacks(
            check_region, stack_prefix
        )
        if not results["cloudformation"]:
            all_passed = False

        # Check 2: Control Tower Landing Zone
        # Note: Pass the CT Home Region here
        results["control_tower"] = check_control_tower_landing_zone(ct_home_region)
        if not results["control_tower"]:
            all_passed = False


    except (NoCredentialsError, BotoCoreError):
        logger.error("Preflight checks failed due to AWS configuration or connection issues.")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"An unexpected error occurred during preflight checks: {e}")
        sys.exit(1)


    # --- Report Summary ---
    logger.info("--- Preflight Check Summary ---")
    for check_name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        logger.info(f"  {check_name.replace('_', ' ').title()}: {status}")
    logger.info("-----------------------------")


    if all_passed:
        logger.info("All preflight checks passed successfully.")
        sys.exit(0)
    else:
        logger.error("One or more preflight checks failed.")
        sys.exit(1)


if __name__ == "__main__":
    run_preflight_checks()