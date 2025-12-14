# TEMS API Gateway - Consumer Test Scripts

This repository provides Python test scripts to demonstrate the complete authentication and consumption flow for the TEMS API Gateway across different trials. These scripts show how consumer applications can authenticate with Keycloak, obtain an API Gateway token, and call protected APIs through the TEMS API Gateway.

## Getting Started

To use these scripts:

1. [Install prerequisites](#prerequisites)

   Python 3 and the `requests` library are required.

2. [Configure environment variables](#environment-configuration)

   Set up your Keycloak client credentials in a `.env` file.

3. [Run the test scripts](#running-the-scripts)

   Execute the script for the trial you want to test.

You can find detailed explanations in the sections below.

## Prerequisites

Before running any script, ensure you have Python 3 installed and the required dependencies:

```bash
pip install requests
```

The scripts use the following Python libraries:
- **requests** - for making HTTP calls to Keycloak and the API Gateway
- **json** - for parsing JSON responses
- **getpass** - for secure password input (password is hidden while typing)

## Environment Configuration

The scripts load Keycloak client credentials from a `.env` file. Create this file in the same directory as the scripts:

```bash
cp .env.example .env
```

Edit the `.env` file with your Keycloak client credentials:

```bash
KEYCLOAK_CLIENT_ID=federated-catalogue
KEYCLOAK_CLIENT_SECRET=your-client-secret-here
```

```
⚠️ Important note:
The .env file contains sensitive credentials and should never be committed to version control.
Make sure it's listed in your .gitignore file.
```

## Available Test Scripts

Each script tests a specific trial configuration with different API endpoints:

| Script | Trial | API Endpoint Tested |
|--------|-------|---------------------|
| `test-trial-1-edmo.py` | Trial 1 - EDMO | `/collections/latest/items?type=string` |
| `test-trial-3-ftv.py` | Trial 3 - France TV | `/healthcheck` |
| `test-trial-3-henneo.py` | Trial 3 - HENNEO | `/healthcheck` |
| `test-trial-8-arctur.py` | Trial 8 - ARCTUR | `/api/core/v1/assets/search` |

## Running the Scripts

Each script follows an interactive flow and will prompt you for the required parameters.

### Example: Testing Trial 1 EDMO

```bash
python3 test-trial-1-edmo.py
```

When you run a script, you'll be prompted to enter:

1. **API Gateway endpoint** - The base URL of the TEMS API Gateway
   ```
   Example: https://api-gateway.tems-dataspace.eu
   ```

2. **Keycloak Username** - Your Keycloak user account
   ```
   Example: consumer@example.com
   ```

3. **Keycloak Password** - Your password (hidden input)
   ```
   The password is not displayed while typing for security
   ```

4. **Agreement ID** - The UUID of the agreement
   ```
   Example: d6e3e361-bd77-46c3-8474-0a67a66512bb
   ```

The script will then execute a complete flow and pause at each step, allowing you to review the results before continuing.

## How the Scripts Work

Each test script follows the same 4-step flow:

### Step 1: Configuration Parameters Collection

The script collects all required parameters interactively:
- API Gateway endpoint URL
- Keycloak username
- Keycloak password (hidden input)
- Agreement ID

### Step 2: Keycloak Authentication

**Endpoint called:**
```
POST https://governance.tems-dataspace.eu/auth/realms/common/protocol/openid-connect/token
```

**Request body:**
```json
{
  "grant_type": "password",
  "client_id": "KEYCLOAK_CLIENT_ID-environment-variable",
  "client_secret": "KEYCLOAK_CLIENT_SECRET-environment-variable",
  "scope": "openid",
  "username": "your-username",
  "password": "your-password"
}
```

**Expected response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI...",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI...",
  "token_type": "Bearer",
  "scope": "openid"
}
```

The script extracts the `access_token` (JWT) from the response and uses it in the next step.

### Step 3: API Gateway Token Retrieval

**Endpoint called:**
```
POST {api_gateway_endpoint}/temsapigateway/token
```

**Request headers:**
```
Authorization: Bearer {jwt_access_token_from_keycloak}
Content-Type: application/json
```

**Request body:**
```json
{
  "agreementId": "d6e3e361-bd77-46c3-8474-0a67a66512bb"
}
```

**Expected response (201 Created):**
```json
{
  "apiGatewayToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "issuedAt": "2025-10-24T12:41:28Z",
  "expiresAt": "2025-10-24T13:41:28Z",
  "agreementId": "d6e3e361-bd77-46c3-8474-0a67a66512bb"
}
```

The script extracts the `apiGatewayToken` and uses it to authenticate API calls through the gateway.

### Step 4: API Test Call through API Gateway

Each script tests a different API endpoint specific to its trial:

#### Trial 1 EDMO - Collections API

**Endpoint called:**
```
GET {api_gateway_endpoint}/collections/latest/items?type=string
```

**Request headers:**
```
X-Api-Gateway-Token: {api_gateway_token}
```

---

#### Trial 3 FTV / HENNEO - Healthcheck API

**Endpoint called:**
```
GET {api_gateway_endpoint}/healthcheck
```

**Request headers:**
```
X-Api-Gateway-Token: {api_gateway_token}
```

---

#### Trial 8 ARCTUR - 3D Heritage Assets Search

**Endpoint called:**
```
GET {api_gateway_endpoint}/api/core/v1/assets/search?query=test&category=1&category=2&historicalPeriod=3&historicalPeriod=4&region=5&region=6&page.page=1&page.pageSize=20&portal=DIKD
```

**Request headers:**
```
X-Api-Gateway-Token: {api_gateway_token}
```

---

**Expected response (200 OK):**
Each API returns its own specific response format. The scripts automatically parse and display:
- JSON responses with proper formatting
- Response status codes
- Content-Type headers
- Error messages if the call fails

## Troubleshooting

### Common Issues

**Issue: "Keycloak login failed! Status code: 401"**
- Check your username and password
- Verify the client_id and client_secret in your `.env` file
- Ensure your Keycloak user account is active

**Issue: "API Gateway token request failed! Status code: 403"**
- Verify the JWT token is valid and not expired
- Check that the Agreement ID exists and is associated with your user
- Ensure you have permission to access this agreement

**Issue: "API call returned an error! Status code: 401"**
- Check that the API Gateway token is valid and not expired
- Verify the token was correctly extracted from the previous step
- Ensure the `X-Api-Gateway-Token` header is being sent

**Issue: Connection timeout or network error**
- Verify the API Gateway endpoint URL is correct
- Check your network connection
- Ensure the API Gateway service is running and accessible
