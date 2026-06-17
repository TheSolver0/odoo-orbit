from odoo import models, fields


class OrbitSprint(models.Model):
    _name = 'orbit.sprint'
    _description = 'Orbit Sprint'

    name = fields.Char(required=True)

    project_id = fields.Many2one(
        'project.project'
    )

    start_date = fields.Date()
    end_date = fields.Date()

    goal = fields.Text()

    status = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed')
    ])

    velocity = fields.Float()

    task_ids = fields.One2many(
        'project.task',
        'sprint_id'
    )