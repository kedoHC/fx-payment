from marshmallow import Schema, fields, validate


class PlainUsersSchema(Schema):
  id = fields.Str(dump_only=True)
  name = fields.Str(required=True)
  email = fields.Str(required=True)
  age = fields.Int(required=True)
  is_active = fields.Boolean(required=True)

class PlainWalletSchema(Schema):
  id = fields.Str(dump_only=True)
  balance = fields.Float(required=True)
  currency = fields.Str(required=True)
  recent_transactions = fields.Int(required=True)
  user_id = fields.Str(dump_only=True)

class UserSchema(PlainUsersSchema):
  wallet = fields.Nested(PlainWalletSchema(), dump_only=True, allow_none=True)
  
class WalletSchema(PlainWalletSchema):
  user = fields.Nested(PlainUsersSchema(), dump_only=True)

class UserListSchema(Schema):
  id = fields.Str(dump_only=True)
  name = fields.Str(dump_only=True)
  email = fields.Str(dump_only=True)
  age = fields.Int(dump_only=True)
  is_active = fields.Boolean(dump_only=True)
  wallet_id = fields.Str(dump_only=True)
  
class WalletListSchema(Schema):
  id = fields.Str(dump_only=True)
  balance = fields.Float(required=True)
  currency = fields.Str(required=True)
  recent_transactions = fields.Int(required=True)
  user = fields.Nested(PlainUsersSchema(), dump_only=True)

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

class CreateUserSchema(Schema):
  name = fields.Str(required=True)
  email = fields.Email(required=True)
  age = fields.Int(required=True, validate=validate.Range(min=1))
  is_active = fields.Bool(load_default=True)

class CreateWalletSchema(Schema):
  user_id = fields.Str(required=True)
  initial_balance = fields.Float(load_default=0.0, validate=validate.Range(min=0))
  currency = fields.Str(load_default="MXN")
