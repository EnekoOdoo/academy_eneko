# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
# C O M E N T A R I O S   D E   E N E K O
#
#
#
##############################################################################
from datetime import datetime, timedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID

ACADEMY_TYPE_LIST = [('public', 'Public'), ('private', 'Private	'), ('concerted', 'Concerted')]


class academy(osv.osv):
    """ Academia """
    _name = 'academy'
    _inherit = 'res.partner'
#### Herencia prototipada (crea un nuevo objeto a partir de res_partner)
    _columns = {        
        'academy_type': fields.selection(ACADEMY_TYPE_LIST, 'Academy Type', help="Select the academy type: public, private, concerted."),  
        'courses_ids':fields.one2many('course', 'academy_id',string="Courses"),      
    }   
 
    _defaults = {'academy_type': 'public',
	}
    
class course(osv.osv):
    """ Curso """
    _name = 'course'
    
    _columns = {
        'academy_id':fields.many2one('academy',required=True, string="Academy"),
        'name':fields.char('Name', size=64,required=True),
        'description':fields.text('Description', required=False),
        'hours':fields.integer('Hours',required=True, help = 'Duration in hours'),
        'max_students':fields.integer('Students Maximum',required=True, help = 'Maximum number of student'),
        'min_students':fields.integer('Students Minimum',required=True, help = 'Minimal number of student'),
        'price':fields.float('Price',(4,2),required=True, help = 'Price of the course'),
        'subject_ids':fields.many2many('subject','course_subject_table',string="Subject", help="Subjects of the course")     
    }
###
#    def onchange_academy_id(self, cr, uid, ids, academy_id, context=None):
#        result = {}
#        if academy_id:
#            academy = self.pool.get('academy').browse(cr, uid, academy_id, context=context)
#            result['academy'] = academy.name
#        return {'value': result}

    
class subject(osv.osv):
    """ Asignaturas """
    _name = 'subject'
    
    _columns = {
        'name':fields.char('Name', size=64,required=True),
        'description':fields.text('Description', required=False),
        'hours':fields.integer('Hours',required=True, help = 'Duration in hours'),        
    }
class res_partner(osv.osv):
    """ Estudiantes """   
    _inherit = 'res.partner'
#### Herencia clásica (extiende objeto res_partner)    
    _columns = {        
        'is_student': fields.boolean('Is Student', help="True if is student"),   
        'is_teacher': fields.boolean('Is Teacher', help="True if is teacher"),     
    }   

	
