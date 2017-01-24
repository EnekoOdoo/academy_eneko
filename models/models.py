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
#IMPORTS
import logging
from datetime import datetime, timedelta
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)

#VARIABLES
COURSE_STATE = [('draft', 'Draft'), ('confirmed', 'Confirmed'), 
                ('in_process', 'In Process'), ('cancel', 'Cancel'),
                 ('done', 'Done')]
TIME_TABLE_TYPE = [('course', 'Course'), ('subject', 'Subject')]
ATTENDANCE_STATE = [('draft', 'Draft'), ('confirmed', 'Confirmed'),
                    ('cancel', 'Cancel'), ('done', 'Done')]
ACADEMY_TYPE_LIST = [('public', 'Public'), ('private', 'Private'), ('concerted', 'Concerted')]
DAY_OF_WEEK = [('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), 
                ('thursday', 'Thursday'), ('friday', 'Friday')]

#CLASES
# Academia 
class res_partner(osv.osv):
    """ Academia """ 
    _inherit = 'res.partner'
    
    def _check_name(self,cr,uid, ids, context=None):
        if context is None:
            context = {}
        
        #Instanciamos el registro que queremos guardar (browse similar antiguo read)       
        current_object = self.browse(cr,uid, ids, context=context)
        
        #Comprobamos que si es una academia no hay el mismo nombre
        if current_object.is_academy:
           #Versión inicial 
           #previous_name_ids = self.search(cr,uid, [('id','!=',current_object.id),('name','=',current_object.name),('is_academy','=',True)], context=context)
            previous_name_ids = self.search(cr,uid, [('id','!=',current_object.id),('name','=ilike',current_object.name),('is_academy','=',True)], context=context)

            if previous_name_ids:
                _logger.info('--------------LOGUEANDO por si acaso. Prueba. No sirve si está bien ----------------')
                _logger.info(previous_name_ids)

                return False
        
        return True    
    
    #### Herencia clásica (extiende objeto res_partner) class academy(osv.osv):
    _columns = {
        'is_academy': fields.boolean('Is Academy',  help="True if is Academy"),   
        'academy_type': fields.selection(ACADEMY_TYPE_LIST, 'Academy Type', help="Select the academy type: public, private, concerted."),  
        'courses_ids':fields.one2many('course', 'academy_id',string="Courses"),
        'is_student': fields.boolean('Is Student', help="True if is student"),  
        'is_teacher': fields.boolean('Is Teacher', help="True if is teacher"), 
        
    }
    
    #Restricción lógica de Odoo a nivel python como equivalente a las de BB.DD.
    _constraints = [
        (_check_name,_("The academy name must be unique"),['name'])
    ]
    
    def onchange_name (self,cr,uid, ids, name, context=None):
        if context is None:
            context = {}
            
        res = {}
       
        if name:
            res['value'] = {'name':name.title()}
            
        return res
 
# Curso
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
        'subject_ids':fields.one2many('course.subject','course_id',string="Subjects", help="Subjects of the course"),
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
 
    """ Asignaturas """

# Asignatura
class subject(osv.osv):
    """ Asignatura """
    _name = 'subject'

    def _check_name(self,cr,uid, ids, context=None):
        if context is None:
            context = {}
        
        #Instanciamos el registro que queremos guardar (browse similar antiguo read)       
        current_object = self.browse(cr,uid, ids, context=context)
        
        previous_name_ids = self.search(cr,uid, [('id','!=',current_object.id),('name','=ilike',current_object.name), context=context)

        if previous_name_ids:
            _logger.info('--------------LOGUEANDO por si acaso. Prueba. No sirve si está bien ----------------')
            _logger.info(previous_name_ids)

            return False
        
        return True    
    
    _columns = {
        'name':fields.char('Name', size=64,required=True),
        'description':fields.text('Description', required=False),
        'hours':fields.integer('Hours',required=True, help = 'Duration in hours'),        
    }
    _constraints = [
        (_check_name,_("The subject name must be unique"),['name'])
    ]
    
    def onchange_name (self,cr,uid, ids, name, context=None):
        if context is None:
            context = {}
            
        res = {}
       
        if name:
            res['value'] = {'name':name.title()}
            
        return res
 
# Horario de cada asignatura del curso
class course_subject(osv.osv):
    """ Horario de cada asignatura del curso"""
    _name = 'course.subject'
    
    _columns = {
        'name':fields.char('Name', size=64,required=True),        
        'course_id': fields.many2one('course', help = "Course",required=True, string="Course", ondelete='restrict'),
        'subject_id': fields.many2one('subject', help = "Subject", required=True, string="Subject", ondelete='restrict'),
        'time_table_id': fields.many2one('time.table', string="Time table detail"),
    }

 # Horario
class time_table(osv.osv):
    """ Horario """  
    _name = 'time.table'

    def _check_name(self,cr,uid, ids, context=None):
        if context is None:
            context = {}
        
        #Instanciamos el registro que queremos guardar (browse similar antiguo read)       
        current_object = self.browse(cr,uid, ids, context=context)
        
        previous_name_ids = self.search(cr,uid, [('id','!=',current_object.id),('name','=ilike',current_object.name), context=context)

        if previous_name_ids:
            _logger.info('--------------LOGUEANDO por si acaso. Prueba. No sirve si está bien ----------------')
            _logger.info(previous_name_ids)

            return False
        
        return True    
    
    _columns = {
        'name':fields.char('Name', size=64,required=True),
        'description':fields.text('Description', required=False),
        'type': fields.selection(TIME_TABLE_TYPE, 'type', help="Type of time table"),
        'time_table_detail_ids':fields.one2many('time.table.detail', 'time_table_id',string="Hours"),
    }
    
    _defaults = {
                'type': TIME_TABLE_TYPE[0][0],
    }
    _constraints = [
        (_check_name,_("The Time Table name must be unique"),['name'])
    ]
    
    def onchange_name (self,cr,uid, ids, name, context=None):
        if context is None:
            context = {}
            
        res = {}
       
        if name:
            res['value'] = {'name':name.title()}
            
        return res
 
# Horario Detalle
class time_table_detail(osv.osv):
    """ Horario Detalle"""
    _name = 'time.table.detail'

    def _check_time_range(self,cr,uid, ids, context=None):
        if context is None:
            context = {}
        
        #Instanciamos el registro que queremos guardar (browse similar antiguo read)       
        current_object = self.browse(cr,uid, ids, context=context)
        
        time_range_ids = self.search(cr,uid, [('id','!=',current_object.id),('time_table_id','=',current_object.time_table_id),('name','=ilike',current_object.name), context=context)

        if time_range_ids:
            _logger.info('--------------LOGUEANDO por si acaso. Prueba. No sirve si está bien ----------------')
            _logger.info(time_range_ids)

            return False
        
        return True    

    
    _columns = {
        'name':fields.char('Name', size=64,required=True),
        'time_table_id': fields.many2one('time.table',required=True, string="Time table detail"),
        'day_of_week': fields.selection(DAY_OF_WEEK, 'Day of the week', help="Day of the week"), 
        'hour_start':fields.float('From',required=True, help = 'Hour of the begin on the day'),  
        'hour_end':fields.float('To',required=True, help = 'Hour of the end on the day'),  
        'sequence':fields.integer('Sequence'),    
    }
    
    _defaults = {
                'sequence': 1,
    }
    
    _constraints = [
        (_check_time_range,_("The Time Table day and hour must be unique"),['day_of_week','hour_start','hour_end'])
    ]

# Asistencia alumnos Cabecera
class student_attendance(osv.osv):
    """ Asistencia alumnos Cabecera """
    _name = 'student.attendance'
   
    _columns = {
        'name':fields.char('Name', required=True, size=128),
        'course_subject_id': fields.many2one('course_subject',required=True, string="Course and Subjects to of the attendance's control"),
        'date_start':fields.date('Start Date',required=True, help = "Date of the begin of the attendance's control"),  
        'date_end':fields.date('End Date',required=True, help = "Date of the end of the attendance's control"),      
        'state': fields.selection(ATTENDANCE_STATE, 'state', help="State of the attendance"),

    } 
    _defaults = {
                'state': ATTENDANCE_STATE[0][0],
    }
 
# Asistencia alumnos Detalle
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
    

