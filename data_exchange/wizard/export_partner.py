# -*- encoding: utf-8 -*-
# =============================================================================
# For copyright and license notices, see __openerp__.py file in root directory
# =============================================================================

from openerp import models, fields, api, _


class WizardExportPartner(models.Model):
    _name = 'wizard.export.partner'

    partner_id = fields.Many2one('res.partner', string=_("Destination"), domain=[('rpc_url', '!=', False)], required=True)
    info = fields.Text(_('Info'), readonly=True)
    state = fields.Selection((
        ('export', 'export'),
        ('end', 'end')
    ), 'state', required=True, translate=False, readonly=True, default='export')

    @api.multi
    def action_start_export(self):
        result = self.env[self._context['active_model']].browse(self._context['active_ids']).sync_remote(self.partner_id)

        wizard_values = {
            'state': 'end',
            'info': result.get('error') or u"Sync completed"
        }
        self.write(wizard_values)

        view_rec = self.env['ir.model.data'].get_object_reference('data_exchange', 'partner_export_form')
        if view_rec:
            view_id = view_rec and view_rec[1] or False

        return {
            'view_type': 'form',
            'name': "Export Partner",
            'view_id': [view_id],
            'res_id': self.id,
            'view_mode': 'form',
            'res_model': 'wizard.export.partner',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }
