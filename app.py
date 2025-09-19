from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def greet():
  """ Say hello to Monato Team!"""
  return {"message": "Hello Monato!"}


if __name__ == '__main__':
  app.run(debug=True, port=5000)