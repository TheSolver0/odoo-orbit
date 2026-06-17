from odoo import models, fields


class OrbitDaily(models.Model):
    """Placeholder – le 'Daily' dans ce workflow est le Tableau Kanban lui-même."""
    _name = 'orbit.daily'
    _description = 'Orbit Daily'

    name = fields.Char(required=True)
