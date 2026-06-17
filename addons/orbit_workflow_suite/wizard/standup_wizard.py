from odoo import models, fields


class StandupWizard(models.TransientModel):
    _name = 'orbit.standup.wizard'
    _description = "Stand-up – Planifier la journée"

    task_ids = fields.Many2many(
        'project.task',
        string="Tâches à planifier",
        domain="[('user_ids', 'in', [uid]), ('planned_for_today', '=', False)]"
    )

    notes = fields.Text(string="Notes du Stand-up")

    def action_plan_today(self):
        stage = self.env.ref('orbit_workflow_suite.stage_today').sudo()
        self.task_ids.write({
            'stage_id': stage.id,
            'planned_for_today': True,
            'standup_comment': self.notes or False,
        })
        return {'type': 'ir.actions.act_window_close'}
