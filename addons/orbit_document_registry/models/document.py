from odoo import models, fields, api

class OrbitDocument(models.Model):
    _name = "orbit.document"
    _description = "Document ORBIT"
    _inherit = [
        "mail.thread",
        "mail.activity.mixin"
    ]

    name = fields.Char(
        string="Référence",
        readonly=True,
        copy=False
    )

    document_type_id = fields.Many2one(
        "orbit.document.type",
        required=True
    )

    client_id = fields.Many2one(
        "res.partner",
        required=True,
        tracking=True
    )

    client_reference = fields.Char(
        string="Référence Client"
    )

    project_name = fields.Char(
        string="Projet"
    )

    version = fields.Integer(
        string="Version",
        default=1,
        copy=False
    )

    transmission_date = fields.Datetime(
        string="Date transmission"
    )

    transmitted_by = fields.Many2one(
        "res.users",
        string="Transmis par"
    )

    objet = fields.Char(
        required=True,
        tracking=True
    )

    date_creation = fields.Date(
        string="Date de création",
        default=fields.Date.today
    )

    auteur_id = fields.Many2one(
        "res.users",
        string="Auteur",
        default=lambda self: self.env.user
    )

    montant_ttc = fields.Float(
        string="Montant TTC"
    )

    attachment = fields.Binary(
        string="Fichier"
    )

    attachment_name = fields.Char(
        string="Nom du fichier"
    )

    onedrive_url = fields.Char(
        string="Lien OneDrive"
    )

    comment = fields.Html(
        string="Commentaires"
    )

    statut = fields.Selection(
        [
            ("draft", "Brouillon"),
            ("sent", "Transmis"),
            ("validated", "Validé"),
            ("cancelled", "Annulé"),
        ],
        default="draft",
        tracking=True
    )

    generated_filename = fields.Char(
        string="Nom de fichier",
        compute="_compute_filename",
        store=True
    )
    
    @api.model
    def create(self, vals):

        if not vals.get("name"):

            doc_type = self.env[
                "orbit.document.type"
            ].browse(vals["document_type_id"])

            year = fields.Date.today().year

            if doc_type.naming_pattern:

                client_name = ""
                if vals.get("client_id"):
                    partner = self.env["res.partner"].browse(vals["client_id"])
                    client_name = (partner.name or "").replace(" ", "")

                objet_clean = (vals.get("objet") or "").replace(" ", "")
                version = vals.get("version", 1)

                num = self.search_count([
                    ("document_type_id", "=", doc_type.id),
                    ("date_creation", ">=", f"{year}-01-01"),
                    ("date_creation", "<=", f"{year}-12-31"),
                ]) + 1

                vals["name"] = doc_type.naming_pattern.format(
                    code=doc_type.code,
                    client=client_name,
                    objet=objet_clean,
                    version=version,
                    num=num,
                    year=year,
                )

            else:

                last_document = self.search(
                    [
                        ("document_type_id", "=", doc_type.id),
                        ("name", "like", f"{doc_type.code}-{year}-%")
                    ],
                    order="id desc",
                    limit=1
                )

                if last_document:

                    last_number = int(
                        last_document.name.split("-")[-1]
                    )

                    sequence = last_number + 1

                else:

                    sequence = 1

                vals["name"] = (
                    f"{doc_type.code}-{year}-{sequence:03d}"
                )

        return super().create(vals)
    
    def action_mark_as_sent(self):

        self.write({
            "statut": "sent",
            "transmission_date": fields.Datetime.now(),
            "transmitted_by": self.env.user.id,
        })

        self.message_post(
            body="Document transmis."
        )
        
    parent_document_id = fields.Many2one(
        "orbit.document",
        string="Document d'origine"
    )

    child_version_ids = fields.One2many(
        "orbit.document",
        "parent_document_id"
    )
    
    def action_create_new_version(self):

        self.ensure_one()

        new_version = self.copy({
            "version": self.version + 1,
            "name": f"{self.name}-v{self.version + 1}",
            "parent_document_id": self.id,
        })

        return {
            "type": "ir.actions.act_window",
            "res_model": "orbit.document",
            "res_id": new_version.id,
            "view_mode": "form",
        }
    def action_validate(self):

        self.write({
            "statut": "validated"
        })

        self.message_post(
            body="Document validé."
        )


    def action_cancel(self):

        self.write({
            "statut": "cancelled"
        })

        self.message_post(
            body="Document annulé."
        )
    
    @api.depends(
        "name",
        "client_id",
        "project_name",
        "version"
    )
    def _compute_filename(self):

        for rec in self:

            client = (
                rec.client_id.name.replace(" ", "_")
                if rec.client_id
                else "CLIENT"
            )

            project = (
                rec.project_name.replace(" ", "_")
                if rec.project_name
                else "DOCUMENT"
            )

            rec.generated_filename = (
                f"{rec.name}_{client}_{project}.pdf"
            )