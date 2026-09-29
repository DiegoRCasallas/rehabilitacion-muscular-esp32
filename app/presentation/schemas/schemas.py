from marshmallow import Schema, fields, validate


class PatientCreateSchema(Schema):
    full_name = fields.Str(required=True)


class ActivityCreateSchema(Schema):
    name = fields.Str(required=True)


class CalibrationCreateSchema(Schema):
    label = fields.Str(required=True)
    rest_amplitude = fields.Float(required=True)
    max_amplitude = fields.Float(required=True)
    base_frequency = fields.Float(required=True)


class SessionStartSchema(Schema):
    patient_id = fields.Int(required=True)
    activity_id = fields.Int(required=True)
    calibration_id = fields.Int(required=True)


class SignalWindowSchema(Schema):
    samples = fields.List(fields.Float(), required=True,
                          validate=validate.Length(min=2))
    sample_rate_hz = fields.Float(required=True,
                                  validate=validate.Range(min=0, min_inclusive=False))


class SessionFinishSchema(Schema):
    windows = fields.List(fields.Nested(SignalWindowSchema), required=True)