 def action_draft_confirmed(self, cr, uid, ids, context=None):
        course_object = self.browse(cr, uid, ids, context=context)
        
        if course_object:
            if course_object.subject_ids:
                hours = 0
                modelo = self.pool.get('subject')                 
               
                for rec in modelo.browse(cr, uid, ids, context=context):
                    hours = [rec.hours] + hours
                    if hours > 0:
                        return True
                
        return False   
