from odoo import models, fields


class OrbitEpic(models.Model):
    _name = 'orbit.epic'
    _description = 'Orbit Epic'

    name = fields.Char(required=True)

    description = fields.Text()

    project_id = fields.Many2one(
        'project.project'
    )

    owner_id = fields.Many2one(
        'res.users'
    )

    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed')
    ])