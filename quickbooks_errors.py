"""
Manejo de errores especializado para QuickBooks API
Incluye parsing de errores QB, clasificación y contexto completo
"""

from enum import Enum
from datetime import datetime
from typing import Dict, Any, Optional

class QBErrorType(Enum):
    """Tipos de errores de QuickBooks"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization" 
    API_LIMIT = "api_limit"
    VALIDATION = "validation"
    NETWORK = "network"
    SYNTAX = "syntax"
    UNKNOWN = "unknown"

class QBError(Exception):
    """Excepción personalizada para errores de QuickBooks"""
    
    def __init__(self, message: str, error_type: QBErrorType, 
                 http_code: int = None, intuit_tid: str = None,
                 qb_error_code: str = None, details: Dict = None):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.http_code = http_code
        self.intuit_tid = intuit_tid
        self.qb_error_code = qb_error_code
        self.details = details or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el error a diccionario para logging"""
        return {
            'message': self.message,
            'error_type': self.error_type.value,
            'http_code': self.http_code,
            'intuit_tid': self.intuit_tid,
            'qb_error_code': self.qb_error_code,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }

class QBErrorHandler:
    """Manejador centralizado de errores de QuickBooks"""
    
    @staticmethod
    def parse_api_error(response) -> QBError:
        """Parsea errores de respuesta API de QuickBooks"""
        intuit_tid = response.headers.get('intuit_tid')
        
        try:
            error_data = response.json()
            fault = error_data.get('Fault', {})
            
            if fault:
                # Estructura de error estándar de QuickBooks
                error = fault.get('Error', [{}])[0]
                error_code = error.get('code', 'unknown')
                error_detail = error.get('Detail', 'No details available')
                
                # Clasificar tipo de error
                error_type = QBErrorHandler._classify_error(response.status_code, error_code)
                
                return QBError(
                    message=error_detail,
                    error_type=error_type,
                    http_code=response.status_code,
                    intuit_tid=intuit_tid,
                    qb_error_code=error_code,
                    details=error_data
                )
            else:
                # Error sin estructura Fault
                return QBError(
                    message=f"HTTP {response.status_code}: {response.text}",
                    error_type=QBErrorHandler._classify_error(response.status_code),
                    http_code=response.status_code,
                    intuit_tid=intuit_tid,
                    details={'raw_response': response.text}
                )
                
        except Exception as e:
            return QBError(
                message=f"Error parsing API response: {str(e)}",
                error_type=QBErrorType.SYNTAX,
                http_code=response.status_code,
                intuit_tid=intuit_tid,
                details={'parse_error': str(e), 'raw_response': response.text}
            )
    
    @staticmethod
    def parse_oauth_error(response) -> QBError:
        """Parsea errores específicos de OAuth"""
        intuit_tid = response.headers.get('intuit_tid')
        
        try:
            error_data = response.json()
            error_code = error_data.get('error', 'unknown_error')
            error_description = error_data.get('error_description', 'No description available')
            
            # Mapear errores OAuth específicos
            if error_code == 'invalid_grant':
                error_type = QBErrorType.AUTHENTICATION
                message = "Refresh token expirado o inválido. Se requiere nueva autorización."
            elif error_code == 'invalid_client':
                error_type = QBErrorType.AUTHENTICATION
                message = "Credenciales de cliente inválidas."
            elif error_code == 'access_denied':
                error_type = QBErrorType.AUTHORIZATION
                message = "Acceso denegado por el usuario."
            else:
                error_type = QBErrorType.AUTHENTICATION
                message = f"OAuth Error: {error_description}"
            
            return QBError(
                message=message,
                error_type=error_type,
                http_code=response.status_code,
                intuit_tid=intuit_tid,
                qb_error_code=error_code,
                details=error_data
            )
            
        except Exception as e:
            return QBError(
                message=f"Error parsing OAuth response: {str(e)}",
                error_type=QBErrorType.SYNTAX,
                http_code=response.status_code,
                intuit_tid=intuit_tid,
                details={'parse_error': str(e), 'raw_response': response.text}
            )
    
    @staticmethod
    def _classify_error(http_code: int, qb_error_code: str = None) -> QBErrorType:
        """Clasifica el tipo de error basado en códigos HTTP y QB"""
        if http_code == 401:
            return QBErrorType.AUTHENTICATION
        elif http_code == 403:
            return QBErrorType.AUTHORIZATION
        elif http_code == 429:
            return QBErrorType.API_LIMIT
        elif http_code == 400:
            if qb_error_code:
                # Códigos específicos de QuickBooks
                if 'validation' in qb_error_code.lower():
                    return QBErrorType.VALIDATION
                elif 'syntax' in qb_error_code.lower() or 'parse' in qb_error_code.lower():
                    return QBErrorType.SYNTAX
            return QBErrorType.VALIDATION
        elif 500 <= http_code < 600:
            return QBErrorType.NETWORK
        else:
            return QBErrorType.UNKNOWN
    
    @staticmethod
    def should_retry(error: QBError) -> bool:
        """Determina si un error debe ser reintentado"""
        # Reintentar errores de red y límites de API
        if error.error_type in [QBErrorType.NETWORK, QBErrorType.API_LIMIT]:
            return True
        
        # Reintentar errores de autenticación solo si es token expirado
        if error.error_type == QBErrorType.AUTHENTICATION:
            return error.qb_error_code in ['invalid_grant', 'token_expired']
        
        return False
    
    @staticmethod
    def get_retry_delay(error: QBError, attempt: int) -> int:
        """Calcula el delay para retry basado en el tipo de error"""
        if error.error_type == QBErrorType.API_LIMIT:
            # Backoff exponencial para límites de API
            return min(60, 2 ** attempt)
        elif error.error_type == QBErrorType.NETWORK:
            # Delay fijo para errores de red
            return 5
        else:
            # Sin delay para otros casos
            return 0
