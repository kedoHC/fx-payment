from marshmallow import Schema, fields



class FundSchema(Schema):
  currency = fields.Str(required=True)
  amount = fields.Float(required=True)

class ConvertSchema(Schema):
  from_currency = fields.Str(required=True)
  to_currency = fields.Str(required=True)
  amount = fields.Float(required=True)

class WithdrawSchema(Schema):
  currency = fields.Str(required=True)
  amount = fields.Float(required=True)