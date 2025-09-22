# FX Payment

A Flask-based REST API for foreign exchange payment processing with support for USD and MXN currencies.

## Features

- 👤 **Create Users** - Create new user accounts with validation
- 💳 **Create Wallets** - Create new wallets for users with initial balance support
- 💰 **Fund Wallet** - Add money to user wallets
- 💸 **Withdraw Funds** - Remove money from wallets with balance validation
- 🔄 **Currency Conversion** - Convert between USD and MXN
- 📊 **Balance Inquiry** - Check wallet balances in both currencies
- ✅ **Comprehensive Testing** - 35+ tests covering all endpoints
- 🐳 **Docker Support** - Easy containerized deployment

## Assumptions

This project operates under the following assumptions:

- 💰 **Storage Currency**: All wallet balances are stored internally in Mexican Pesos (MXN)
- 🌍 **Supported Currencies**: Only MXN (Mexican Peso) and USD (US Dollar) are supported for funding, withdrawals, and conversions
- 💱 **Fixed Exchange Rate**: The conversion rate is fixed at **1 USD = 18.70 MXN**
- 🔄 **Automatic Conversion**: When funding or withdrawing in USD, amounts are automatically converted to/from MXN for storage
- 📈 **Balance Display**: The `/balances` endpoint returns amounts in both MXN (stored value) and USD (converted value)

## Quick Start

```bash
# Clone and setup
git clone git@github.com:kedoHC/fx-payment.git
cd fx-payment

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The API will be available at `http://localhost:5001`

## Installation

### 1. Create the virtual environment

```bash
python3 -m venv venv
```

### 2. Activate the virtual environment

**On macOS/Linux:**

```bash
source venv/bin/activate
```

**On Windows (Command Prompt or PowerShell):**

```cmd
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Start the Application

```bash
python app.py
```

The application will start on `http://localhost:5001`

### API Endpoints

The FX Payment API provides the following endpoints:

#### User Management
- **POST** `/users` - Create a new user account

#### Wallet Management
- **POST** `/wallets` - Create a new wallet for a user
- **POST** `/wallets/<user_id>/fund` - Add funds to a wallet (USD amounts automatically converted to MXN for storage)
- **POST** `/wallets/<user_id>/withdraw` - Withdraw funds from a wallet (USD amounts converted to MXN for balance validation)
- **POST** `/wallets/<user_id>/convert` - Convert between USD and MXN currencies
- **GET** `/wallets/<user_id>/balances` - Get wallet balances displayed in both MXN (stored) and USD (converted)

**Supported Currencies:** USD, MXN (only)  
**Fixed Exchange Rate:** 1 USD = 18.70 MXN  
**Storage:** All balances stored in MXN

### Example API Requests

#### Creating a User
```bash
# Create a new user
curl -X POST http://localhost:5001/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com", "age": 30}'

# Response: {"message": "User created successfully", "user_id": "generated-uuid"}
```

#### Creating a Wallet
```bash
# Create a wallet for the user (with $100 USD initial balance)
curl -X POST http://localhost:5001/wallets \
  -H "Content-Type: application/json" \
  -d '{"user_id": "f9e8d7c6-b5a4-43f2-1e0d-9c8b7a6f5e4d", "initial_balance": 100.0, "currency": "USD"}'

# Response: {"message": "Wallet created successfully", "user_id": "f9e8d7c6-b5a4-43f2-1e0d-9c8b7a6f5e4d"}
```

#### Funding and Checking Balances
```bash
# Fund a wallet with $100 USD (will be stored as 1,870 MXN)
curl -X POST http://localhost:5001/wallets/f9e8d7c6-b5a4-43f2-1e0d-9c8b7a6f5e4d/fund \
  -H "Content-Type: application/json" \
  -d '{"currency": "USD", "amount": 100.0}'

# Response: {"message": "Amount added successfully"}

# Check wallet balances (returns both MXN stored amount and USD equivalent)
curl http://localhost:5001/wallets/f9e8d7c6-b5a4-43f2-1e0d-9c8b7a6f5e4d/balances

# Response: {"mxn": 1870.0, "usd": 100.0}
```

## Testing

This project includes comprehensive test coverage for all API endpoints. Follow these steps to run the tests:

### Prerequisites

Make sure you have activated your virtual environment and installed all dependencies:

```bash
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

### Running Tests

#### Run All Tests

To run the complete test suite covering all services:

```bash
pytest -v tests/
```

#### Run Tests by Service

You can run tests for individual services:

**Create User Service Tests (8 tests):**

```bash
pytest -v tests/create_user_test.py
```

**Create Wallet Service Tests (9 tests):**

```bash
pytest -v tests/create_wallet_test.py
```

**Fund Service Tests (5 tests):**

```bash
pytest -v tests/fund_test.py
```

**Convert Service Tests (4 tests):**

```bash
pytest -v tests/convert_test.py
```

**Withdraw Service Tests (4 tests):**

```bash
pytest -v tests/withdraw_test.py
```

**Balances Service Tests (3 tests):**

```bash
pytest -v tests/balances_test.py
```

#### Run Specific Test

To run a specific test function:

```bash
pytest -v tests/fund_test.py::test_fund_wallet_success
```

### Expected Output

When running all tests, you should see output similar to:

```bash
$ pytest -v tests/
==================================================== test session starts =====================================================
platform darwin -- Python 3.9.6, pytest-8.4.2, pluggy-1.6.0 -- /path/to/venv/bin/python3
cachedir: .pytest_cache
rootdir: /path/to/fx-payment
plugins: flask-1.3.0
collected 16 items

tests/balances_test.py::test_get_balances_success PASSED                                                               [  6%]
tests/balances_test.py::test_get_balances_user_not_found PASSED                                                        [ 12%]
tests/balances_test.py::test_get_balances_zero_balance PASSED                                                          [ 18%]
tests/convert_test.py::test_convert_currency_success PASSED                                                            [ 25%]
tests/convert_test.py::test_convert_currency_user_not_found PASSED                                                     [ 31%]
tests/convert_test.py::test_convert_currency_invalid_json PASSED                                                       [ 37%]
tests/convert_test.py::test_convert_currency_malformed_json PASSED                                                     [ 43%]
tests/fund_test.py::test_fund_wallet_success PASSED                                                                    [ 50%]
tests/fund_test.py::test_fund_wallet_user_not_found PASSED                                                             [ 56%]
tests/fund_test.py::test_fund_wallet_invalid_json PASSED                                                               [ 62%]
tests/fund_test.py::test_fund_wallet_no_json_data PASSED                                                               [ 68%]
tests/fund_test.py::test_fund_wallet_empty_json_data PASSED                                                            [ 75%]
tests/withdraw_test.py::test_withdraw_wallet_success PASSED                                                            [ 81%]
tests/withdraw_test.py::test_withdraw_wallet_insufficient_balance PASSED                                               [ 87%]
tests/withdraw_test.py::test_withdraw_wallet_invalid_json PASSED                                                       [ 93%]
tests/withdraw_test.py::test_withdraw_wallet_malformed_json PASSED                                                     [100%]

===================================================== 16 passed in 0.12s =====================================================
```

✅ **All 16 tests should pass** - If any tests fail, check that your virtual environment is activated and dependencies are installed.

### Test Coverage

The test suite covers:

- ✅ **Success scenarios** (200 responses)
- ✅ **User not found** (404 responses)
- ✅ **Validation errors** (422 responses)
- ✅ **Malformed JSON** (400 responses)
- ✅ **Business logic** (insufficient balance, currency conversion)
- ✅ **Edge cases** (zero balance, different currencies)

**Total: 33 tests** across all endpoints

### Test Structure

Each test file follows a consistent pattern:

- `create_user_test.py` - Tests for `/users` endpoint (8 tests)
- `create_wallet_test.py` - Tests for `/wallets` endpoint (9 tests)
- `fund_test.py` - Tests for `/wallets/<user_id>/fund` endpoint (5 tests)
- `convert_test.py` - Tests for `/wallets/<user_id>/convert` endpoint (4 tests)
- `withdraw_test.py` - Tests for `/wallets/<user_id>/withdraw` endpoint (4 tests)
- `balances_test.py` - Tests for `/wallets/<user_id>/balances` endpoint (3 tests)

## Project Structure

- `app.py` - Main Flask application
- `requirements.txt` - Project dependencies
- `venv/` - Python virtual environment
- `tests/` - Test suite
  - `create_user_test.py` - User creation endpoint tests
  - `create_wallet_test.py` - Wallet creation endpoint tests
  - `fund_test.py` - Fund wallet endpoint tests
  - `convert_test.py` - Currency conversion endpoint tests
  - `withdraw_test.py` - Withdraw wallet endpoint tests
  - `balances_test.py` - Balance retrieval endpoint tests
- `utils/` - Utility functions
  - `converter.py` - Currency conversion logic
  - `validate_user.py` - User validation
  - `validate_balance.py` - Balance validation
- `store/` - Data storage
  - `users.py` - User data
  - `wallets.py` - Wallet data
- `schemas.py` - Data validation schemas

## Docker Usage

### Build the Docker Image

```bash
docker build -t fx-payment .
```

### Run the Container

```bash
docker run -p 5005:5000 fx-payment
```

The application will be available at `http://localhost:5005`

### Development Mode (Optional)

For development with live code reloading:

```bash
docker run -p 5005:5000 -w /app -v "$(pwd):/app" fx-payment
```
