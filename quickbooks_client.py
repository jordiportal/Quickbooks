"""
Cliente para la API de QuickBooks Online
Este módulo proporciona funciones para conectarse a QuickBooks Online y obtener datos de ventas.
"""

import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class QuickBooksClient:
    """Cliente para interactuar con la API de QuickBooks Online"""
    
    def __init__(self):
        self.client_id = os.getenv('QB_CLIENT_ID')
        self.client_secret = os.getenv('QB_CLIENT_SECRET')
        self.redirect_uri = os.getenv('QB_REDIRECT_URI')
        self.base_url = os.getenv('QB_SANDBOX_BASE_URL', 'https://sandbox-quickbooks.api.intuit.com')
        self.access_token = None
        self.refresh_token = None
        self.company_id = None
        
    def get_auth_url(self) -> str:
        """
        Genera la URL de autorización para OAuth 2.0
        Returns:
            str: URL de autorización de QuickBooks
        """
        scope = 'com.intuit.quickbooks.accounting'
        state = 'security_token'  # En producción, usar un token seguro aleatorio
        
        auth_url = (
            f"https://appcenter.intuit.com/connect/oauth2?"
            f"client_id={self.client_id}&"
            f"scope={scope}&"
            f"redirect_uri={self.redirect_uri}&"
            f"response_type=code&"
            f"access_type=offline&"
            f"state={state}"
        )
        
        return auth_url
    
    def exchange_code_for_tokens(self, authorization_code: str, realm_id: str) -> bool:
        """
        Intercambia el código de autorización por tokens de acceso
        Args:
            authorization_code: Código de autorización recibido del callback
            realm_id: ID de la compañía (company ID)
        Returns:
            bool: True si el intercambio fue exitoso
        """
        token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': self.redirect_uri
        }
        
        try:
            response = requests.post(
                token_url,
                headers=headers,
                data=data,
                auth=(self.client_id, self.client_secret)
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                self.refresh_token = token_data.get('refresh_token')
                self.company_id = realm_id
                return True
            else:
                print(f"Error obteniendo tokens: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"Error en intercambio de tokens: {str(e)}")
            return False
    
    def refresh_access_token(self) -> bool:
        """
        Refresca el token de acceso usando el refresh token
        Returns:
            bool: True si el refresh fue exitoso
        """
        if not self.refresh_token:
            return False
            
        token_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        
        try:
            response = requests.post(
                token_url,
                headers=headers,
                data=data,
                auth=(self.client_id, self.client_secret)
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                self.refresh_token = token_data.get('refresh_token')
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Error refrescando token: {str(e)}")
            return False
    
    def make_api_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """
        Realiza una petición a la API de QuickBooks
        Args:
            endpoint: Endpoint de la API (ej: 'items', 'customers')
            params: Parámetros de consulta opcionales
        Returns:
            Dict: Respuesta de la API o None si hay error
        """
        if not self.access_token or not self.company_id:
            print("No hay tokens de acceso o company_id configurados")
            return None
        
        url = f"{self.base_url}/v3/company/{self.company_id}/{endpoint}"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                # Token expirado, intentar refrescar
                if self.refresh_access_token():
                    headers['Authorization'] = f'Bearer {self.access_token}'
                    response = requests.get(url, headers=headers, params=params)
                    if response.status_code == 200:
                        return response.json()
                
            print(f"Error en API request: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            print(f"Error realizando petición: {str(e)}")
            return None
    
    def get_sales_receipts(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """
        Obtiene recibos de venta del período especificado
        Args:
            start_date: Fecha de inicio (YYYY-MM-DD)
            end_date: Fecha de fin (YYYY-MM-DD)
        Returns:
            List[Dict]: Lista de recibos de venta
        """
        # Si no se especifican fechas, obtener del mes actual
        if not start_date or not end_date:
            today = datetime.now()
            start_date = today.replace(day=1).strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')
        
        query = f"SELECT * FROM SalesReceipt WHERE TxnDate >= '{start_date}' AND TxnDate <= '{end_date}'"
        params = {'query': query}
        
        result = self.make_api_request('query', params)
        
        if result and 'QueryResponse' in result:
            return result['QueryResponse'].get('SalesReceipt', [])
        
        return []
    
    def get_invoices(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """
        Obtiene facturas del período especificado
        Args:
            start_date: Fecha de inicio (YYYY-MM-DD)
            end_date: Fecha de fin (YYYY-MM-DD)
        Returns:
            List[Dict]: Lista de facturas
        """
        if not start_date or not end_date:
            today = datetime.now()
            start_date = today.replace(day=1).strftime('%Y-%m-%d')
            end_date = today.strftime('%Y-%m-%d')
        
        query = f"SELECT * FROM Invoice WHERE TxnDate >= '{start_date}' AND TxnDate <= '{end_date}'"
        params = {'query': query}
        
        result = self.make_api_request('query', params)
        
        if result and 'QueryResponse' in result:
            return result['QueryResponse'].get('Invoice', [])
        
        return []
    
    def get_monthly_sales_summary(self, year: int = None, month: int = None) -> Dict:
        """
        Obtiene un resumen de ventas del mes especificado
        Args:
            year: Año (por defecto año actual)
            month: Mes (por defecto mes actual)
        Returns:
            Dict: Resumen de ventas del mes
        """
        if not year or not month:
            today = datetime.now()
            year = today.year
            month = today.month
        
        # Calcular fechas del mes
        start_date = datetime(year, month, 1).strftime('%Y-%m-%d')
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)
        end_date = end_date.strftime('%Y-%m-%d')
        
        # Obtener datos
        sales_receipts = self.get_sales_receipts(start_date, end_date)
        invoices = self.get_invoices(start_date, end_date)
        
        # Calcular totales
        total_sales_receipts = sum(float(receipt.get('TotalAmt', 0)) for receipt in sales_receipts)
        total_invoices = sum(float(invoice.get('TotalAmt', 0)) for invoice in invoices)
        
        summary = {
            'período': f"{month:02d}/{year}",
            'fecha_inicio': start_date,
            'fecha_fin': end_date,
            'recibos_de_venta': {
                'cantidad': len(sales_receipts),
                'total': total_sales_receipts
            },
            'facturas': {
                'cantidad': len(invoices),
                'total': total_invoices
            },
            'total_ventas': total_sales_receipts + total_invoices,
            'detalle_transacciones': {
                'recibos': sales_receipts,
                'facturas': invoices
            }
        }
        
        return summary