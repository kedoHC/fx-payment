
def converter(amount, from_currency, to_currency='MXN'):
  """
    Assumptions:
    1 USD = 18.70 MXN
    1 MXN = 0.053 USD
    The portfolio balance will always be saved in MXN
  """
  MXN_TO_USD = 18.70

  if isinstance(amount, (int, float)):
    if from_currency == 'MXN' and to_currency == "USD":
      print("here")
      return amount / MXN_TO_USD
    elif from_currency == 'USD' and to_currency == "MXN":
      return amount *  MXN_TO_USD
    elif from_currency == 'MXN' and to_currency == "MXN":
      return amount
    else:
      return None
  else:
    return None





