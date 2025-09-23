transactions_log = [
  {
    "transaction_id": "a1b2c3d4-e5f6-7g8h-9i0j-k1l2m3n4o5p6",
    "user_id": "6d1f3e2a-0b9c-4d5e-8f7a-2b3c4d5e6f7a", # Bob
    "type": "deposit",
    "amount": 100.00,
    "currency": "MXN",
    "timestamp": "2025-09-19T10:00:00Z",
    "status": "completed"
  },
  {
    "transaction_id": "b2c3d4e5-f6g7-h8i9-j0k1-l2m3n4o5p6q7",
    "user_id": "2e0a8b9f-1d4e-4c7a-9b6d-3f0e1c2a8b9d", # Alice
    "type": "withdraw",
    "amount": 50.00,
    "currency": "MXN",
    "timestamp": "2025-09-19T11:30:00Z",
    "status": "completed"
  },
  {
    "transaction_id": "c3d4e5f6-g7h8-i9j0-k1l2-m3n4o5p6q7r8",
    "user_id": "6d1f3e2a-0b9c-4d5e-8f7a-2b3c4d5e6f7a", # Bob
    "type": "send",
    "amount": 25.50,
    "currency": "MXN",
    "recipient_id": "a4b5c6d7-e8f9-40a1-8b2c-3d4e5f6a7b8c", # Charlie
    "timestamp": "2025-09-19T12:45:00Z",
    "status": "pending"
  }
]