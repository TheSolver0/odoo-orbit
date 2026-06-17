from odoo import models, fields

class OrbitDocumentType(models.Model):
    _name = "orbit.document.type"
    _description = "Type de document"

    name = fields.Char(required=True)
    code = fields.Char(required=True)
    active = fields.Boolean(default=True)
    naming_pattern = fields.Char(
        string="Modèle de nom",
        help=(
            "Modèle de génération du nom du document.\n"
            "Variables disponibles :\n"
            "  {code}    → code du type (ex: FP)\n"
            "  {client}  → nom du client sans espaces\n"
            "  {objet}   → objet du document sans espaces\n"
            "  {version} → numéro de version (ex: 1)\n"
            "  {num:03d} → numéro séquentiel annuel (ex: 001)\n"
            "  {year}    → année (ex: 2026)\n"
            "Exemples :\n"
            "  FP_{client}_{objet}_v{version}\n"
            "  Offre_{objet}_{client}_v{version}\n"
            "  FACT_{num:03d}_{client}_{year}"
        ),
    )