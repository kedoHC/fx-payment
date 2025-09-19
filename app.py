from flask import Flask, jsonify, request
from utils.converter import converter
from store.wallets import wallets_data

app = Flask(__name__)
URL_BASE = "/wallets"

@app.get("/")
def greet():
  """ Say hello to Monato Team!"""

  return {"message": "Hello Monato!"}

@app.post(URL_BASE + "/<user_id>/fund")
def fund_wallet(user_id):
  """ fun wallet by user id"""

  request_data = request.get_json()
  if user_id in wallets_data:
    amount_to_mx = converter(request_data['amount'], request_data['currency'])
    wallets_data[user_id]['balance'] += amount_to_mx
    return {"message": "Amount added successfully"}
  else:
    return {"message": "User not found"}, 404

if __name__ == '__main__':
  app.run(debug=True, port=5001)