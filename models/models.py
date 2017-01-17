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

COURSE_STATE = [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('in_process', 'In Process'), ('cancel', 'Cancel'), ('done', 'Done')]
ATTENDANCE_STATE = [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('cancel', 'Cancel'), ('done', 'Done')]

ACADEMY_TYPE_LIST = [('public', 'Public'), ('private', 'Private'), ('concerted', 'Concerted')]

DAY_OF_WEEK = [('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), ('thursday', 'Thursday'), ('friday', 'Friday')]
class res_partner(osv.osv):
    """ Academia """   
    _inherit = 'res.partner'
    #### Herencia clásica (extiende objeto res_partner)    class academy(osv.osv):
    _columns = {
        'is_academy': fields.boolean('Is Academy',  help="True if is Academy"),   
        'academy_type': fields.selection(ACADEMY_TYPE_LIST, 'Academy Type', help="Select the academy type: public, private, concerted."),  
        'courses_ids':fields.one2many('course', 'academy_id',string="Courses"),
        'is_student': fields.boolean('Is Student', help="True if is student"),  
        'is_teacher': fields.boolean('Is Teacher', help="True if is teacher"),        
   
    }   
 
class course(osv.osv):
    """ Curso """
    _name = 'course'
    
    _columns = {
        'academy_id':fields.many2one('res.partner',required=True, domain =[('is_academy','=',True)], string="Academy",ondelete='restrict'),
        'time_table_id': fields.many2one('time.table', help = "Time table of courses", string="Time Table", ondelete='restrict'),
        'name':fields.char('Name', size=64,required=True),
        'description':fields.text('Description', required=False),
        'hours':fields.integer('Hours',required=True, help = 'Duration in hours'),
        'date_start':fields.date('Start Date',required=True, help = 'Date of the begin of the course'),  
        'date_end':fields.date('End Date',required=True, help = 'Date of the end of the course'),      
        'max_students':fields.integer('Students Maximum',required=True, help = 'Maximum number of student'),
        'min_students':fields.integer('Students Minimum',required=True, help = 'Minimal number of student'),
        'price':fields.float('Price',(4,2),required=True, help = 'Price of the course'),
        'subject_ids':fields.many2many('subject','course_subject_table',string="Subjects", help="Subjects of the course"),
        'student_ids':fields.many2many('res.partner','course_student_table', domain =[('is_student','=',True)],string="Students", help="Students of the course"),
        'teacher_ids':fields.many2many('res.partner','teacher_student_table', domain =[('is_teacher','=',True)],string="Teachers", help="Teachers of the course"),
        'state': fields.selection(COURSE_STATE, 'state', help="State of the course"),
    }
    
    _defaults = {
                'state': COURSE_STATE[0][0],
    }
    
    def action_draft(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        self.write (cr, uid, ids, {'state': 'draft'})
        return True
        
    def action_confirmed(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        self.write (cr, uid, ids, {'state': 'confirmed'})
        return True
    
    def signal_confirmed(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        self.signal_workflow(cr, uid, ids,'button_confirmed') #Dispara el signal del WF. Ejemplo de disparo WF indirecto
        return True
        
    def action_draft_confirmed(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        course_object = self.browse(cr, uid, ids, context=context)         
        
        if course_object:
            if course_object.subject_ids:
                return True
                
        return False   

    def action_in_process(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        self.write (cr, uid, ids, {'state': 'in_process'})
        return True
        
    def action_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        self.write (cr, uid, ids, {'state': 'cancel'})
        return True
        
    def action_done(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        self.write (cr, uid, ids, {'state': 'done'})
        return True

   
class subject(osv.osv):
    """ Asignaturas """
    _name = 'subject'
    
    _columns = {
        'name':fields.char('Name', size=64,required=True),
        'description':fields.text('Description', required=False),
        'hours':fields.integer('Hours',required=True, help = 'Duration in hours'),        
    }

   
class time_table(osv.osv):
    """ Horario """
    _name = 'time.table'
    
    _columns = {
        'name':fields.char('Name', size=64,required=True),
        'description':fields.text('Description', required=False),
        'time_table_detail_ids':fields.one2many('time.table.detail', 'time_table_id',string="Hours"),
    }

class time_table_detail(osv.osv):
    """ Horario Detalle"""
    _name = 'time.table.detail'
    
    _columns = {
        'name':fields.char('Name', size=64,required=True),
        'time_table_id': fields.many2one('time.table',required=True, string="Time table detail"),
        'day_of_week': fields.selection(DAY_OF_WEEK, 'Day of the week', help="Day of the week"), 
        'hour_start':fields.float('From',required=True, help = 'Hour of the begin on the day'),  
        'hour_end':fields.float('To',required=True, help = 'Hour of the end on the day'),      
    }       
class student_attendance(osv.osv):
    """ Asistencia alumnos Cabecera """
    _name = 'student.attendance'
    
    _columns = {
        'name':fields.char('Name', required=True, size=128),
        'course_id': fields.many2one('course',required=True, string="Course to of the attendance's control"),
        'subject_id': fields.many2one('subject',required=True, string="Subject of the attendance's control"),
        'date_start':fields.date('Start Date',required=True, help = "Date of the begin of the attendance's control"),  
        'date_end':fields.date('End Date',required=True, help = "Date of the end of the attendance's control"),      
        'state': fields.selection(ATTENDANCE_STATE, 'state', help="State of the attendance"),

    } 
    _defaults = {
                'state': ATTENDANCE_STATE[0][0],
    }
class student_attendance_detail(osv.osv):
    """ Asistencia alumnos Detalle """
    _name = 'student.attendance.detail'
    
    _columns = {
        'name':fields.char('Name', required=True, size=64),
        'attendance_id': fields.many2one('student.attendance',required=True, string="The attendance's control"),
        'student_id': fields.many2one('res.partner',required=True,domain =[('is_student','=',True)], string="Student to the attendance's control"),
        'attendance_date':fields.date('Date of attendance',required=True, help = "Date of the attendance"),  
        'sign': fields.boolean(string="sign"),
    } 
    
    _defaults = {
                'sign': False,
    }
