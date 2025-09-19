from store.wallets import wallets_data


def validate_balance(id, amount):
  """ Check if the user has sufficient balance in his account """

  return wallets_data[id]['balance'] >= amount
