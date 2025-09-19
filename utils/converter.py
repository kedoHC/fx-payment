
def converter(amount, from_currency, to_currency='MXN'):
  """
    Vamos a asumir que:
    1 USD = 18.70 MXN
    1 MXN = 0.053 USD
    y que el saldo siempre será guardado en MXN
  """
  USD_MXN = 18.70
  MXN_USD = 0.053

  if isinstance(amount, (int, float)):
    if from_currency == 'MXN' and to_currency == "USD":
      return amount * MXN_USD
    elif from_currency == 'USD' and to_currency == "MXN":
      return amount * USD_MXN
    else: 
      return None
  else:
    return None





