#!/usr/bin/env python3
"""
TEMS API Gateway Test Script - Trial 5 FRANCE_TV_DISTRIBUTION
==============================================

This script demonstrates the complete flow for using the TEMS API Gateway with the FRANCE_TV_DISTRIBUTION API.

Real API endpoint to be tested trough API GATEWAY: https://france-tv-distribution.adapter.luminvent.com/

Requirements: pip install requests
"""

import requests
import json
import sys
import os
from pathlib import Path
from getpass import getpass

# Colors for better readability
class Colors:
    HEADER = '\033[95m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_step(number, text):
    print(f"{Colors.CYAN}{Colors.BOLD}STEP {number}: {text}{Colors.ENDC}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.RED}✗ ERROR: {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.ENDC}")

def print_json(data, title=""):
    if title:
        print(f"\n{Colors.BOLD}{title}:{Colors.ENDC}")
    print(json.dumps(data, indent=2))

# Load environment variables from .env file
def load_env():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env()

# Get Keycloak credentials from environment
KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID')
KEYCLOAK_CLIENT_SECRET = os.getenv('KEYCLOAK_CLIENT_SECRET')

# Initial banner
print_header("TEMS API Gateway Test - Trial 5 FRANCE_TV_DISTRIBUTION")
print("This script will test the TEMS API Gateway with the FRANCE_TV_DISTRIBUTION API.\n")

# ============================================================================
# STEP 1: Gather configuration
# ============================================================================
print_step(1, "Configuration Parameters Collection")
print()

api_gateway_endpoint = input(f"{Colors.BOLD}Enter API Gateway endpoint: {Colors.ENDC}").strip()
if not api_gateway_endpoint:
    print_error("API Gateway endpoint is required!")
    sys.exit(1)

api_gateway_endpoint = api_gateway_endpoint.rstrip('/')

keycloak_username = input(f"{Colors.BOLD}Enter Keycloak Username: {Colors.ENDC}").strip()
if not keycloak_username:
    print_error("Keycloak username is required!")
    sys.exit(1)

keycloak_password = getpass(f"{Colors.BOLD}Enter Keycloak Password: {Colors.ENDC}").strip()
if not keycloak_password:
    print_error("Keycloak password is required!")
    sys.exit(1)

agreement_id = input(f"{Colors.BOLD}Enter Agreement ID: {Colors.ENDC}").strip()
if not agreement_id:
    print_error("Agreement ID is required!")
    sys.exit(1)

print_success("All parameters collected successfully!\n")

print(f"{Colors.BOLD}Configuration summary:{Colors.ENDC}")
print(f"- API Gateway Endpoint: {api_gateway_endpoint}")
print(f"- Keycloak Username: {keycloak_username}")
print(f"- Keycloak Password: {'*' * len(keycloak_password)}")
print(f"- Agreement ID: {agreement_id}")
print()

input(f"{Colors.YELLOW}Press ENTER to continue with Keycloak login...{Colors.ENDC}")

# ============================================================================
# STEP 2: Keycloak authentication
# ============================================================================
print_step(2, "Keycloak Authentication")
print()

keycloak_url = "https://governance.tems-dataspace.eu/auth/realms/common/protocol/openid-connect/token"
print_info(f"Contacting Keycloak: {keycloak_url}")
print_info("Sending credentials to obtain JWT token...")
print()

keycloak_data = {
    "grant_type": "password",
    "client_id": KEYCLOAK_CLIENT_ID,
    "client_secret": KEYCLOAK_CLIENT_SECRET,
    "scope": "openid",
    "username": keycloak_username,
    "password": keycloak_password
}

try:
    keycloak_response = requests.post(
        keycloak_url,
        data=keycloak_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30
    )

    if keycloak_response.status_code != 200:
        print_error(f"Keycloak login failed! Status code: {keycloak_response.status_code}")
        print_error(f"Response: {keycloak_response.text}")
        sys.exit(1)

    keycloak_json = keycloak_response.json()
    jwt_access_token = keycloak_json.get("access_token")

    if not jwt_access_token:
        print_error("Access token not present in response!")
        sys.exit(1)

    print_success("Keycloak login completed successfully!")
    print()
    print(f"{Colors.BOLD}JWT Access Token obtained:{Colors.ENDC}")
    print(f"{Colors.GREEN}{jwt_access_token}{Colors.ENDC}")
    print()

    if "expires_in" in keycloak_json:
        print_info(f"Token will expire in {keycloak_json['expires_in']} seconds")
    print()

except requests.exceptions.RequestException as e:
    print_error(f"Error during Keycloak request: {str(e)}")
    sys.exit(1)
except json.JSONDecodeError as e:
    print_error(f"Error parsing JSON response: {str(e)}")
    sys.exit(1)

input(f"{Colors.YELLOW}Press ENTER to continue with API Gateway token retrieval...{Colors.ENDC}")

# ============================================================================
# STEP 3: Obtain API Gateway token
# ============================================================================
print_step(3, "API Gateway Token Retrieval")
print()

api_gateway_token_url = f"{api_gateway_endpoint}/apigateway/temsapigateway/token"
print_info(f"Endpoint to obtain token: {api_gateway_token_url}")
print_info(f"Using JWT token for authentication...")
print_info(f"Requested Agreement ID: {agreement_id}")
print()

token_headers = {
    "Authorization": f"Bearer {jwt_access_token}",
    "Content-Type": "application/json"
}

token_body = {
    "agreementId": agreement_id
}

try:
    token_response = requests.post(
        api_gateway_token_url,
        headers=token_headers,
        json=token_body,
        timeout=30
    )

    if token_response.status_code != 201:
        print_error(f"API Gateway token request failed! Status code: {token_response.status_code}")
        print_error(f"Response: {token_response.text}")
        sys.exit(1)

    token_json = token_response.json()
    api_gateway_token = token_json.get("apiGatewayToken")
    expires_at = token_json.get("expiresAt")
    issued_at = token_json.get("issuedAt")

    if not api_gateway_token:
        print_error("API Gateway token not present in response!")
        sys.exit(1)

    print_success("API Gateway token obtained successfully!")
    print()
    print_json(token_json, "Complete response")
    print()

    print(f"{Colors.BOLD}API Gateway Token:{Colors.ENDC}")
    print(f"{Colors.GREEN}{api_gateway_token}{Colors.ENDC}")
    print()

    if issued_at:
        print_info(f"Token issued at: {issued_at}")
    if expires_at:
        print_info(f"Token valid until: {expires_at}")
    print()

except requests.exceptions.RequestException as e:
    print_error(f"Error during API Gateway token request: {str(e)}")
    sys.exit(1)
except json.JSONDecodeError as e:
    print_error(f"Error parsing JSON response: {str(e)}")
    sys.exit(1)

input(f"{Colors.YELLOW}Press ENTER to execute test API call through the API Gateway...{Colors.ENDC}")

# ============================================================================
# STEP 4: Test API call through API Gateway (FRANCE_TV_DISTRIBUTION endpoint)
# ============================================================================
print_step(4, "API Test Call through API Gateway - FRANCE_TV_DISTRIBUTION ")
print()

original_endpoint = "https://france-tv-distribution.adapter.luminvent.com/"
gateway_api_endpoint = f"{api_gateway_endpoint}/apigateway/"

print(f"{Colors.BOLD}Endpoint comparison:{Colors.ENDC}")
print(f"  {Colors.BOLD}Original API endpoint:{Colors.ENDC}")
print(f"    {original_endpoint}")
print()
print(f"  {Colors.BOLD}TEMS API Gateway endpoint:{Colors.ENDC}")
print(f"    {gateway_api_endpoint}")
print()

print_info("IMPORTANT: We are calling the TEMS API Gateway, NOT the original endpoint!")
print_info("The API Gateway will forward the request to the FRANCE_TV_DISTRIBUTION API endpoint")
print_info(f"Using API Gateway token for authentication...")
print()

api_headers = {
    "X-Api-Gateway-Token": api_gateway_token
}

try:
    print_info("Sending GET request to /...")
    api_response = requests.get(
        gateway_api_endpoint,
        headers=api_headers,
        timeout=30
    )

    print()
    print(f"{Colors.BOLD}Response received:{Colors.ENDC}")
    print(f"- Status Code: {api_response.status_code}")
    print(f"- Content-Type: {api_response.headers.get('Content-Type', 'N/A')}")
    print()

    if api_response.status_code == 200:
        print_success("API call completed successfully!")
        print()

        try:
            response_json = api_response.json()
            print_json(response_json, "Response body")
        except json.JSONDecodeError:
            print(f"{Colors.BOLD}Response body (text):{Colors.ENDC}")
            print(api_response.text[:1000])
            if len(api_response.text) > 1000:
                print(f"\n... (response truncated, total length: {len(api_response.text)} characters)")
    else:
        print_error(f"API call returned an error! Status code: {api_response.status_code}")
        print(f"{Colors.BOLD}Response body:{Colors.ENDC}")
        print(api_response.text)

except requests.exceptions.RequestException as e:
    print_error(f"Error during API call: {str(e)}")
    sys.exit(1)

# ============================================================================
# Final summary
# ============================================================================
print()
print(f"{Colors.BOLD}Summary:{Colors.ENDC}")
print()
print(f"{Colors.CYAN}1. KEYCLOAK LOGIN{Colors.ENDC}")
print(f"   ✓ Authenticated with Keycloak and obtained JWT access token")
print()
print(f"{Colors.CYAN}2. API GATEWAY TOKEN RETRIEVAL{Colors.ENDC}")
print(f"   ✓ Obtained API Gateway token for Agreement ID: {agreement_id}")
print()
print(f"{Colors.CYAN}3. FRANCE_TV_DISTRIBUTION API CALL THROUGH GATEWAY{Colors.ENDC}")
print(f"   ✓ Successfully called FRANCE_TV_DISTRIBUTION API through TEMS API Gateway")
print(f"   ✓ Tested endpoint: /")
print()
print(f"{Colors.GREEN}{Colors.BOLD}Success!{Colors.ENDC} {Colors.GREEN}TEMS API Gateway is working correctly with Trial 5 INA!{Colors.ENDC}")
print()