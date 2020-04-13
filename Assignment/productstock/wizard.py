from openerp.osv import orm, fields
from openerp.tools.translate import _

class wiz_student_report(orm.TransientModel):
    _name = 'wiz.student.report'
    _columns = {
        'student_id': fields.many2one('student.master', 'Student Name'),
        'birth_sdate': fields.date('Start Date'),
        'birth_edate': fields.date('End Date'),
    }

    def student_report(self, cr, uid, ids, context=None):
        student_obj = self.pool.get('student.master')
        cur_obj = self.browse(cr, uid, ids, context=context)
        datas = {}
        if cur_obj.birth_sdate >= cur_obj.birth_edate:
            raise orm.except_orm(_('Warning!'),_('End date is %s must be greater then start date is %s') % (cur_obj.birth_edate,cur_obj.birth_sdate))
        student_ids = student_obj.search(cr, uid, [('fname', '=', cur_obj.student_id.fname),('dob','>=',cur_obj.birth_sdate),('dob','<=',cur_obj.birth_edate)], context=context)
        if student_ids:
            data = self.read(cr, uid, ids, context=context)[0]
            datas = {
            'ids': student_ids,
            'model': 'wiz.student.report', # wizard model name
            'form': data,
            'context':context
            }
            return {
                   'type': 'ir.actions.report.xml',
                   'report_name': 'school_management.report_student_master_qweb',#module name.report template name
                   'datas': datas,
               }