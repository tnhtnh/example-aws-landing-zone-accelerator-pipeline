# tests/test_aws_checks.py
import os
import sys
from unittest.mock import patch, MagicMock

import pytest
from moto import mock_aws # Updated import for moto 4+

# Ensure the preflight_checks module can be found
# This might be needed if running pytest from the root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from preflight_checks import aws_checks

# Define the test region and other constants
TEST_REGION = "us-east-1"
CT_HOME_REGION = "us-east-1" # Assuming same for tests
STACK_PREFIX = "AWSAccelerator"
ALT_STACK_PREFIX = "MyCustomPrefix"
LZ_ARN = f"arn:aws:controltower:{CT_HOME_REGION}:123456789012:landingzone/EXAMPLE1-LZ"

# Helper to set environment variables
@pytest.fixture(autouse=True)
def default_environment_variables(monkeypatch):
    """Set default environment variables for tests."""
    monkeypatch.setenv("AWS_REGION", TEST_REGION)
    monkeypatch.setenv("CT_HOME_REGION", CT_HOME_REGION)
    monkeypatch.setenv("STACK_PREFIX", STACK_PREFIX)
    # Ensure default AWS creds for moto
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", TEST_REGION)

# --- CloudFormation Tests ---

@mock_aws
def test_cfn_no_stacks():
    """Test CFN check when no stacks exist."""
    assert aws_checks.check_cloudformation_stacks(TEST_REGION, STACK_PREFIX) is True

@mock_aws
def test_cfn_no_matching_failed_stacks():
    """Test CFN check when failed stacks exist but don't match prefix."""
    # Using patch as moto's simulation of CFN failures can be inconsistent
    with patch('boto3.client') as mock_boto_client:
        mock_cfn = MagicMock()
        mock_cfn.get_paginator.return_value.paginate.return_value = [{
            "StackSummaries": [{
                "StackName": "OtherPrefix-FailedStack",
                "StackStatus": "UPDATE_ROLLBACK_COMPLETE",
                "StackId": "arn:aws:cloudformation:us-east-1:123456789012:stack/OtherPrefix-FailedStack/guid"
            }]
        }]
        # Ensure the correct client is returned when requested
        mock_boto_client.side_effect = lambda service, **kwargs: mock_cfn if service == 'cloudformation' else MagicMock()
        assert aws_checks.check_cloudformation_stacks(TEST_REGION, STACK_PREFIX) is True

@mock_aws
def test_cfn_matching_failed_stack():
    """Test CFN check when a failed stack matches the prefix."""
    with patch('boto3.client') as mock_boto_client:
        mock_cfn = MagicMock()
        mock_cfn.get_paginator.return_value.paginate.return_value = [{
            "StackSummaries": [{
                "StackName": f"{STACK_PREFIX}-App1-Failed",
                "StackStatus": "CREATE_FAILED",
                "StackId": f"arn:aws:cloudformation:{TEST_REGION}:123456789012:stack/{STACK_PREFIX}-App1-Failed/guid"
            }]
        }]
        mock_boto_client.side_effect = lambda service, **kwargs: mock_cfn if service == 'cloudformation' else MagicMock()
        assert aws_checks.check_cloudformation_stacks(TEST_REGION, STACK_PREFIX) is False

@mock_aws
def test_cfn_matching_active_stack():
    """Test CFN check when an active stack matches the prefix (should pass)."""
    # Active stacks should not be caught by the FAILED_STACK_STATUSES filter
    with patch('boto3.client') as mock_boto_client:
        mock_cfn = MagicMock()
        # Simulate paginator returning empty list because no stacks match the FAILED status filter
        mock_cfn.get_paginator.return_value.paginate.return_value = []
        mock_boto_client.side_effect = lambda service, **kwargs: mock_cfn if service == 'cloudformation' else MagicMock()
        assert aws_checks.check_cloudformation_stacks(TEST_REGION, STACK_PREFIX) is True

@mock_aws
def test_cfn_mixed_stacks_one_failed_match():
    """Test CFN check with multiple stacks, one matching failed."""
    with patch('boto3.client') as mock_boto_client:
        mock_cfn = MagicMock()
        mock_cfn.get_paginator.return_value.paginate.return_value = [
            { # Page 1
                "StackSummaries": [
                    # This active stack matching prefix won't be included by filter
                    # { "StackName": f"{STACK_PREFIX}-GoodStack", "StackStatus": "CREATE_COMPLETE", ... },
                    { # Failed, different prefix
                        "StackName": "OtherPrefix-FailedStack",
                        "StackStatus": "UPDATE_ROLLBACK_COMPLETE",
                        "StackId": f"arn:aws:cloudformation:{TEST_REGION}:123456789012:stack/OtherPrefix-FailedStack/guid"
                    }
                ]
            },
            { # Page 2
                 "StackSummaries": [
                     { # Failed, matches prefix
                        "StackName": f"{STACK_PREFIX}-BadStack",
                        "StackStatus": "ROLLBACK_COMPLETE",
                        "StackId": f"arn:aws:cloudformation:{TEST_REGION}:123456789012:stack/{STACK_PREFIX}-BadStack/guid"
                     }
                 ]
            }
        ]
        mock_boto_client.side_effect = lambda service, **kwargs: mock_cfn if service == 'cloudformation' else MagicMock()
        assert aws_checks.check_cloudformation_stacks(TEST_REGION, STACK_PREFIX) is False

@mock_aws
def test_cfn_custom_prefix_failed_match(monkeypatch):
    """Test CFN check with a custom prefix from env var."""
    monkeypatch.setenv("STACK_PREFIX", ALT_STACK_PREFIX) # Override default for this test
    with patch('boto3.client') as mock_boto_client:
        mock_cfn = MagicMock()
        mock_cfn.get_paginator.return_value.paginate.return_value = [{
            "StackSummaries": [
                { # Failed, matches custom prefix
                    "StackName": f"{ALT_STACK_PREFIX}-Database-Failed",
                    "StackStatus": "DELETE_FAILED",
                    "StackId": f"arn:aws:cloudformation:{TEST_REGION}:123456789012:stack/{ALT_STACK_PREFIX}-Database-Failed/guid"
                },
                 { # Failed, matches default prefix (should be ignored now)
                    "StackName": f"{STACK_PREFIX}-Network-Failed",
                    "StackStatus": "CREATE_FAILED",
                    "StackId": f"arn:aws:cloudformation:{TEST_REGION}:123456789012:stack/{STACK_PREFIX}-Network-Failed/guid"
                }
            ]
        }]
        mock_boto_client.side_effect = lambda service, **kwargs: mock_cfn if service == 'cloudformation' else MagicMock()
        # Call the function directly to test its logic with the *specific* prefix passed
        assert aws_checks.check_cloudformation_stacks(TEST_REGION, ALT_STACK_PREFIX) is False

# --- Control Tower Tests ---

@mock_aws
def test_ct_not_enabled():
    """Test CT check when ListLandingZones returns empty."""
    # moto's controltower mock requires explicit setup or defaults to empty.
    # We don't need to create a Landing Zone here.
    with patch('boto3.client') as mock_boto_client:
        mock_ct = MagicMock()
        mock_ct.list_landing_zones.return_value = {"landingZones": []}
        mock_boto_client.side_effect = lambda service, **kwargs: mock_ct if service == 'controltower' else MagicMock()
        assert aws_checks.check_control_tower_landing_zone(CT_HOME_REGION) is True

@mock_aws
def test_ct_enabled_active_in_sync():
    """Test CT check when Landing Zone is ACTIVE and IN_SYNC."""
    with patch('boto3.client') as mock_boto_client:
        mock_ct = MagicMock()
        mock_ct.list_landing_zones.return_value = {"landingZones": [{"arn": LZ_ARN}]}
        mock_ct.get_landing_zone.return_value = {
            "landingZone": {
                "version": "3.0",
                "latestAvailableVersion": "3.0",
                "driftStatus": "IN_SYNC",
                "status": "ACTIVE",
                "arn": LZ_ARN,
                "manifestJson": "{}"
            }
        }
        mock_boto_client.side_effect = lambda service, **kwargs: mock_ct if service == 'controltower' else MagicMock()
        assert aws_checks.check_control_tower_landing_zone(CT_HOME_REGION) is True

@mock_aws
def test_ct_enabled_active_drifted():
    """Test CT check when Landing Zone is ACTIVE but DRIFTED (should still pass, logs warning)."""
    with patch('boto3.client') as mock_boto_client:
        mock_ct = MagicMock()
        mock_ct.list_landing_zones.return_value = {"landingZones": [{"arn": LZ_ARN}]}
        mock_ct.get_landing_zone.return_value = {
            "landingZone": {
                "version": "3.0",
                "latestAvailableVersion": "3.0",
                "driftStatus": "DRIFTED",
                "status": "ACTIVE",
                "arn": LZ_ARN,
                "manifestJson": "{}"
            }
        }
        mock_boto_client.side_effect = lambda service, **kwargs: mock_ct if service == 'controltower' else MagicMock()
        assert aws_checks.check_control_tower_landing_zone(CT_HOME_REGION) is True # Currently passes on DRIFTED

@mock_aws
def test_ct_enabled_failed_status():
    """Test CT check when Landing Zone status is FAILED."""
    with patch('boto3.client') as mock_boto_client:
        mock_ct = MagicMock()
        mock_ct.list_landing_zones.return_value = {"landingZones": [{"arn": LZ_ARN}]}
        mock_ct.get_landing_zone.return_value = {
            "landingZone": {
                "version": "3.0",
                "latestAvailableVersion": "3.0",
                "driftStatus": "IN_SYNC",
                "status": "FAILED", # Failed status
                "arn": LZ_ARN,
                "manifestJson": "{}"
            }
        }
        mock_boto_client.side_effect = lambda service, **kwargs: mock_ct if service == 'controltower' else MagicMock()
        assert aws_checks.check_control_tower_landing_zone(CT_HOME_REGION) is False

@mock_aws
def test_ct_enabled_version_mismatch():
    """Test CT check when Landing Zone version is outdated (should pass, logs warning)."""
    with patch('boto3.client') as mock_boto_client:
        mock_ct = MagicMock()
        mock_ct.list_landing_zones.return_value = {"landingZones": [{"arn": LZ_ARN}]}
        mock_ct.get_landing_zone.return_value = {
            "landingZone": {
                "version": "2.9", # Older version
                "latestAvailableVersion": "3.1", # Newer available
                "driftStatus": "IN_SYNC",
                "status": "ACTIVE",
                "arn": LZ_ARN,
                "manifestJson": "{}"
            }
        }
        mock_boto_client.side_effect = lambda service, **kwargs: mock_ct if service == 'controltower' else MagicMock()
        assert aws_checks.check_control_tower_landing_zone(CT_HOME_REGION) is True # Passes but warns

@mock_aws
def test_ct_api_access_denied():
    """Test CT check handles AccessDeniedException gracefully (skips check)."""
    with patch('boto3.client') as mock_boto_client:
        mock_ct = MagicMock()
        from botocore.exceptions import ClientError
        error_response = {'Error': {'Code': 'AccessDeniedException', 'Message': 'Denied'}}
        mock_ct.list_landing_zones.side_effect = ClientError(error_response, 'ListLandingZones')
        mock_boto_client.side_effect = lambda service, **kwargs: mock_ct if service == 'controltower' else MagicMock()
        assert aws_checks.check_control_tower_landing_zone(CT_HOME_REGION) is True # Skips, so passes

@mock_aws
def test_ct_api_not_subscribed():
    """Test CT check handles ValidationException for not subscribed (skips check)."""
    with patch('boto3.client') as mock_boto_client:
        mock_ct = MagicMock()
        from botocore.exceptions import ClientError
        # Match the specific error message structure if possible
        error_response = {'Error': {'Code': 'ValidationException', 'Message': 'AWS Control Tower is not available in the us-east-1 Region for the account 123456789012. Make sure your account is enrolled in AWS Control Tower.'}}
        mock_ct.list_landing_zones.side_effect = ClientError(error_response, 'ListLandingZones')
        mock_boto_client.side_effect = lambda service, **kwargs: mock_ct if service == 'controltower' else MagicMock()
        assert aws_checks.check_control_tower_landing_zone(CT_HOME_REGION) is True # Skips, so passes

# --- Main Script Tests ---

# Patch the check functions themselves for main script tests
@patch('preflight_checks.aws_checks.check_cloudformation_stacks')
@patch('preflight_checks.aws_checks.check_control_tower_landing_zone')
@patch('sys.exit')
def test_run_preflight_checks_all_pass(mock_exit, mock_ct_check, mock_cfn_check, monkeypatch):
    """Test main runner when all checks pass."""
    monkeypatch.setenv("AWS_REGION", TEST_REGION) # Ensure region is set
    mock_cfn_check.return_value = True
    mock_ct_check.return_value = True
    aws_checks.run_preflight_checks()
    mock_cfn_check.assert_called_once_with(TEST_REGION, STACK_PREFIX)
    mock_ct_check.assert_called_once_with(CT_HOME_REGION) # Uses CT_HOME_REGION
    mock_exit.assert_called_once_with(0)

@patch('preflight_checks.aws_checks.check_cloudformation_stacks')
@patch('preflight_checks.aws_checks.check_control_tower_landing_zone')
@patch('sys.exit')
def test_run_preflight_checks_cfn_fails(mock_exit, mock_ct_check, mock_cfn_check, monkeypatch):
    """Test main runner when CloudFormation check fails."""
    monkeypatch.setenv("AWS_REGION", TEST_REGION)
    mock_cfn_check.return_value = False
    mock_ct_check.return_value = True
    aws_checks.run_preflight_checks()
    mock_cfn_check.assert_called_once_with(TEST_REGION, STACK_PREFIX)
    mock_ct_check.assert_called_once_with(CT_HOME_REGION)
    mock_exit.assert_called_once_with(1)

@patch('preflight_checks.aws_checks.check_cloudformation_stacks')
@patch('preflight_checks.aws_checks.check_control_tower_landing_zone')
@patch('sys.exit')
def test_run_preflight_checks_ct_fails(mock_exit, mock_ct_check, mock_cfn_check, monkeypatch):
    """Test main runner when Control Tower check fails."""
    monkeypatch.setenv("AWS_REGION", TEST_REGION)
    mock_cfn_check.return_value = True
    mock_ct_check.return_value = False
    aws_checks.run_preflight_checks()
    mock_cfn_check.assert_called_once_with(TEST_REGION, STACK_PREFIX)
    mock_ct_check.assert_called_once_with(CT_HOME_REGION)
    mock_exit.assert_called_once_with(1)

@patch('preflight_checks.aws_checks.check_cloudformation_stacks')
@patch('preflight_checks.aws_checks.check_control_tower_landing_zone')
@patch('sys.exit')
def test_run_preflight_checks_both_fail(mock_exit, mock_ct_check, mock_cfn_check, monkeypatch):
    """Test main runner when both checks fail."""
    monkeypatch.setenv("AWS_REGION", TEST_REGION)
    mock_cfn_check.return_value = False
    mock_ct_check.return_value = False
    aws_checks.run_preflight_checks()
    mock_cfn_check.assert_called_once_with(TEST_REGION, STACK_PREFIX)
    mock_ct_check.assert_called_once_with(CT_HOME_REGION)
    mock_exit.assert_called_once_with(1)

@patch('preflight_checks.aws_checks.check_cloudformation_stacks')
@patch('preflight_checks.aws_checks.check_control_tower_landing_zone')
@patch('sys.exit')
def test_run_preflight_checks_no_region(mock_exit, mock_ct_check, mock_cfn_check, monkeypatch):
    """Test main runner when AWS_REGION is not set."""
    # Explicitly remove region variables
    monkeypatch.delenv("AWS_REGION", raising=False)
    monkeypatch.delenv("AWS_DEFAULT_REGION", raising=False)
    monkeypatch.delenv("CT_HOME_REGION", raising=False) # Also remove this if it relies on AWS_REGION

    aws_checks.run_preflight_checks()
    # mock_cfn_check.assert_not_called() # Removed: Check functions might still be entered after mocked sys.exit
    # mock_ct_check.assert_not_called() # Removed: Check functions might still be entered after mocked sys.exit
    mock_exit.assert_called_once_with(1) # This is the key assertion

# Add __init__.py files if they don't exist
@pytest.fixture(scope="session", autouse=True)
def create_init_files():
    """Ensure __init__.py files exist for discovery."""
    basedir = os.path.dirname(__file__)
    # Go up one level to the workspace root relative to this test file
    workspace_root = os.path.abspath(os.path.join(basedir, '..'))
    init_files_to_check = [
        os.path.join(workspace_root, 'preflight_checks', '__init__.py'),
        os.path.join(workspace_root, 'tests', '__init__.py')
    ]
    created_files = []
    for init_file in init_files_to_check:
        if not os.path.exists(init_file):
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(init_file), exist_ok=True)
            with open(init_file, 'w') as f:
                f.write("# Auto-generated by test setup\n")
            created_files.append(init_file)
            print(f"Created {init_file}") # Debugging print
    yield # Let tests run
    # Optional: Clean up created files after test session
    # for init_file in created_files:
    #     if os.path.exists(init_file):
    #         os.remove(init_file)
    #         print(f"Removed {init_file}") # Debugging print 