# FX Payment

A Flask application for foreign exchange payment processing.

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

```bash
python app.py
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

**Total: 16 tests** across all endpoints

### Test Structure

Each test file follows a consistent pattern:

- `fund_test.py` - Tests for `/wallets/<user_id>/fund` endpoint
- `convert_test.py` - Tests for `/wallets/<user_id>/convert` endpoint
- `withdraw_test.py` - Tests for `/wallets/<user_id>/withdraw` endpoint
- `balances_test.py` - Tests for `/wallets/<user_id>/balances` endpoint

## Project Structure

- `app.py` - Main Flask application
- `requirements.txt` - Project dependencies
- `venv/` - Python virtual environment
- `tests/` - Test suite
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

## Docker usage

```bash
docker build - fx-payment .
```

```bash
docker run -p 5005:5000 fx-payment
```

[Optional] Use for development process

```bash
docker run -p 5005:5000 -w /app -v "$(pwd):/app" fx-payment
```
