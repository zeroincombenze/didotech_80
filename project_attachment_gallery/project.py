# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 - TODAY Denero Team. (<http://www.deneroteam.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields
from openerp.osv import osv
from openerp.tools.translate import _


class project_project(osv.osv):
    _inherit = 'project.project'

    def _get_attached_images(self, cr, uid, ids, name, args, context=None):
        result = dict([(id, {}) for id in ids])
        attachment = self.pool.get("ir.attachment")
        for id in ids:
            attachment_ids = attachment.search(
                cr, uid, [
                    ('res_model', '=', 'project.project'),
                    ('res_id', '=', id), ('file_type', 'ilike', 'image')
                ],
                context=context
            )
            result[id]['image_ids'] = attachment_ids

            # Set Task images
            task_ids = self.pool.get('project.task').search(
                cr, uid, [('project_id', '=', id)], context=context
            )
            task_image_ids = attachment.search(
                cr, uid, [
                    ('res_model', '=', 'project.task'),
                    ('res_id', 'in', task_ids),
                    ('file_type', 'ilike', 'image')
                ],
                context=context
            )
            result[id]['task_image_ids'] = task_image_ids

            # set issue images
            issue_ids = self.pool.get('project.issue').search(
                cr, uid, [
                    '|', ('project_id', '=', id),  ('task_id', 'in', task_ids)
                ],
                context=context
            )

            issue_image_ids = attachment.search(
                cr, uid, [
                    ('res_model', '=', 'project.issue'),
                    ('res_id', 'in', issue_ids),
                    ('file_type', 'ilike', 'image')
                ],
                context=context
            )
            result[id]['issue_image_ids'] = issue_image_ids
        return result

    def _get_attached_documents(self, cr, uid, ids, name, args, context=None):
        result = dict([(id, {}) for id in ids])
        attachment = self.pool.get("ir.attachment")
        for id in ids:
            attachment_ids = attachment.search(
                cr, uid, [
                    ('res_model', '=', 'project.project'),
                    ('res_id', '=', id),
                    ('file_type', 'not ilike', 'image')
                ],
                context=context
            )
            result[id]['document_ids'] = attachment_ids

            # Set Task images
            task_ids = self.pool.get('project.task').search(cr, uid, [('project_id', '=', id)], context=context)
            task_image_ids = attachment.search(
                cr, uid, [
                    ('res_model', '=', 'project.task'),
                    ('res_id', 'in', task_ids),
                    ('file_type', 'not ilike', 'image')
                ],
                context=context
            )
            result[id]['task_document_ids'] = task_image_ids

            # set issue images
            issue_ids = self.pool.get('project.issue').search(
                cr, uid, ['|', ('project_id', '=', id),  ('task_id', 'in', task_ids)], context=context
            )
            issue_image_ids = attachment.search(
                cr, uid, [
                    ('res_model', '=', 'project.issue'),
                    ('res_id', 'in', issue_ids),
                    ('file_type', 'not ilike', 'image')
                ],
                context=context
            )
            result[id]['issue_document_ids'] = issue_image_ids
        return result
    _columns = {
        'image_ids': fields.function(
            _get_attached_images, relation='ir.attachment', type="one2many", string="Images", multi="image"
        ),
        'document_ids': fields.function(
            _get_attached_documents, relation='ir.attachment', type="one2many", string="Documents", multi="docs"
        ),
        'task_image_ids': fields.function(
            _get_attached_images, relation='ir.attachment', type="one2many", string="Images", multi="image"
        ),
        'task_document_ids': fields.function(
            _get_attached_documents, relation='ir.attachment', type="one2many", string="Documents", multi="docs"
        ),
        'issue_image_ids': fields.function(
            _get_attached_images, relation='ir.attachment', type="one2many", string="Images", multi="image"
        ),
        'issue_document_ids': fields.function(
            _get_attached_documents, relation='ir.attachment', type="one2many", string="Documents", multi="docs"
        ),

    }


class project_task(osv.osv):
    _inherit = "project.task"

    def _get_attached_images(self, cr, uid, ids, name, args, context=None):
        result = {}
        attachment = self.pool.get("ir.attachment")
        for id in ids:
            attachment_ids = attachment.search(
                cr, uid, [
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', id),
                    ('file_type', 'ilike', 'image')
                ],
                context=context
            )
            result[id] = attachment_ids
        return result

    def _get_attached_documents(self, cr, uid, ids, name, args, context=None):
        result = {}
        attachment = self.pool.get("ir.attachment")
        for id in ids:
            attachment_ids = attachment.search(
                cr, uid, [
                    ('res_model', '=', 'project.task'),
                    ('res_id', '=', id),
                    ('file_type', 'not ilike', 'image')
                ],
                context=context
            )
            result[id] = attachment_ids
        return result
    _columns = {
        'image_ids': fields.function(
            _get_attached_images, relation='ir.attachment', type="one2many", string="Images"
        ),
        'document_ids': fields.function(
            _get_attached_documents, relation='ir.attachment', type="one2many", string="Documents"
        ),
    }


class project_issue(osv.osv):
    _inherit = "project.issue"

    def _get_attached_images(self, cr, uid, ids, name, args, context=None):
        result = {}
        attachment = self.pool.get("ir.attachment")
        for id in ids:
            attachment_ids = attachment.search(
                cr, uid, [
                    ('res_model', '=', 'project.issue'),
                    ('res_id', '=', id),
                    ('file_type', 'ilike', 'image')
                ],
                context=context
            )
            result[id] = attachment_ids
        return result

    def _get_attached_documents(self, cr, uid, ids, name, args, context=None):
        result = {}
        attachment = self.pool.get("ir.attachment")
        for id in ids:
            attachment_ids = attachment.search(
                cr, uid, [
                    ('res_model', '=', 'project.issue'),
                    ('res_id', '=', id),
                    ('file_type', 'not ilike', 'image')
                ],
                context=context
            )
            result[id] = attachment_ids
        return result
    _columns = {
        'image_ids': fields.function(
            _get_attached_images, relation='ir.attachment', type="one2many", string="Images"
        ),
        'document_ids': fields.function(
            _get_attached_documents, relation='ir.attachment', type="one2many", string="Documents"
        ),
    }
