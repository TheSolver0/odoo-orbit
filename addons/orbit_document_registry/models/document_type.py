from odoo import models, fields

class OrbitDocumentType(models.Model):
    _name = "orbit.document.type"
    _description = "Type de document"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    active = fields.Boolean(default=True)