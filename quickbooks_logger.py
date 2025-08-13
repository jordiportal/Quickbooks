"""
Sistema de logging especializado para QuickBooks API
Captura intuit_tid y maneja logs estructurados para troubleshooting
"""

import logging
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

class QuickBooksLogger:
    """Sistema de logging especializado para QuickBooks API"""
    
    def __init__(self):
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Configura el sistema de logging"""
        # Crear directorio de logs si no existe
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        
        # Configurar logger
        logger = logging.getLogger('quickbooks_api')
        logger.setLevel(logging.DEBUG)
        
        # Evitar duplicar handlers
        if logger.handlers:
            return logger
        
        # Handler para archivo general
        file_handler = logging.FileHandler(
            f'{log_dir}/quickbooks_api.log',
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Handler para errores críticos
        error_handler = logging.FileHandler(
            f'{log_dir}/quickbooks_errors.log',
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        
        # Formato de log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)
        
        # Console handler para desarrollo
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def log_api_request(self, method: str, url: str, params: Dict = None, 
                       headers: Dict = None, response_code: int = None,
                       response_headers: Dict = None, intuit_tid: str = None,
                       duration_ms: float = None):
        """Log de petición API con intuit_tid"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'type': 'api_request',
            'method': method,
            'url': url,
            'params': params,
            'response_code': response_code,
            'intuit_tid': intuit_tid,
            'duration_ms': duration_ms
        }
        
        # Ocultar tokens en headers
        safe_headers = self._sanitize_headers(headers) if headers else None
        if safe_headers:
            log_data['headers'] = safe_headers
            
        if response_headers:
            log_data['response_headers'] = dict(response_headers)
        
        if response_code and response_code >= 400:
            self.logger.error(f"API Request Failed: {json.dumps(log_data, indent=2)}")
        else:
            self.logger.info(f"API Request: {method} {url} - Code: {response_code} - TID: {intuit_tid}")
            
        # Log detallado para debugging
        self.logger.debug(f"API Request Details: {json.dumps(log_data, indent=2)}")
    
    def log_oauth_flow(self, action: str, success: bool, error_code: str = None, 
                      error_description: str = None, state_token: str = None,
                      intuit_tid: str = None):
        """Log del flujo OAuth"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'type': 'oauth_flow',
            'action': action,
            'success': success,
            'state_token': state_token[:8] + '...' if state_token else None,
            'intuit_tid': intuit_tid
        }
        
        if not success:
            log_data['error_code'] = error_code
            log_data['error_description'] = error_description
            self.logger.error(f"OAuth Error: {json.dumps(log_data, indent=2)}")
        else:
            self.logger.info(f"OAuth Success: {action} - TID: {intuit_tid}")
    
    def log_error(self, error_type: str, error_message: str, context: Dict = None,
                 intuit_tid: str = None, exception: Exception = None,
                 qb_error_code: str = None, http_code: int = None):
        """Log de errores con contexto completo"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'type': 'error',
            'error_type': error_type,
            'error_message': error_message,
            'intuit_tid': intuit_tid,
            'qb_error_code': qb_error_code,
            'http_code': http_code,
            'context': context or {}
        }
        
        if exception:
            log_data['exception_type'] = type(exception).__name__
            log_data['exception_details'] = str(exception)
        
        self.logger.error(f"Error Details: {json.dumps(log_data, indent=2)}")
    
    def log_performance(self, operation: str, duration_ms: float, 
                       records_processed: int = None, company_id: str = None):
        """Log de rendimiento"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'type': 'performance',
            'operation': operation,
            'duration_ms': duration_ms,
            'records_processed': records_processed,
            'company_id': company_id
        }
        
        self.logger.info(f"Performance: {json.dumps(log_data)}")
    
    def log_cache_operation(self, operation: str, cache_hit: bool, 
                          company_id: str = None, period: str = None):
        """Log de operaciones de cache"""
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'type': 'cache',
            'operation': operation,
            'cache_hit': cache_hit,
            'company_id': company_id,
            'period': period
        }
        
        self.logger.info(f"Cache: {json.dumps(log_data)}")
    
    def _sanitize_headers(self, headers: Dict) -> Dict:
        """Oculta información sensible de headers"""
        safe_headers = headers.copy()
        sensitive_keys = ['Authorization', 'authorization', 'Bearer', 'token']
        
        for key in safe_headers:
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                safe_headers[key] = '***HIDDEN***'
        
        return safe_headers

# Instancia global del logger
qb_logger = QuickBooksLogger()
