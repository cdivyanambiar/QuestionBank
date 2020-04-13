'''
Created on Jun 21, 2017

@author: nambidiv
'''
import logging


LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}
LOG_FILENAME = 'logging_QuestionReader.out'
LOG_LEVEL=LEVELS.get('info', logging.NOTSET)

class LogQuestionCreator:
    def __init__(self):         
        logging.basicConfig(filename=LOG_FILENAME,
                    level=LOG_LEVEL,
                    )   
    def log_error(self,logmsg):        
        logging.error(logmsg)   
    
    def log_info(self,logmsg):  
        logging.info(logmsg)  