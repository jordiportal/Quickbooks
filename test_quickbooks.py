"""
Tests básicos para verificar la funcionalidad de QuickBooks Online
"""

import os
import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from quickbooks_client import QuickBooksClient

class TestQuickBooksClient(unittest.TestCase):
    """Tests para el cliente de QuickBooks"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.client = QuickBooksClient()
        self.client.client_id = "test_client_id"
        self.client.client_secret = "test_client_secret"
        self.client.redirect_uri = "http://localhost:5000/callback"
    
    def test_init(self):
        """Test de inicialización del cliente"""
        self.assertIsNotNone(self.client.client_id)
        self.assertIsNotNone(self.client.client_secret)
        self.assertIsNotNone(self.client.redirect_uri)
        self.assertIsNotNone(self.client.base_url)
    
    def test_get_auth_url(self):
        """Test de generación de URL de autorización"""
        auth_url = self.client.get_auth_url()
        
        self.assertIn("appcenter.intuit.com", auth_url)
        self.assertIn("client_id=test_client_id", auth_url)
        self.assertIn("scope=com.intuit.quickbooks.accounting", auth_url)
        self.assertIn("redirect_uri=http://localhost:5000/callback", auth_url)
    
    @patch('quickbooks_client.requests.post')
    def test_exchange_code_for_tokens_success(self, mock_post):
        """Test de intercambio exitoso de código por tokens"""
        # Mock de respuesta exitosa
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token'
        }
        mock_post.return_value = mock_response
        
        result = self.client.exchange_code_for_tokens('test_code', 'test_realm_id')
        
        self.assertTrue(result)
        self.assertEqual(self.client.access_token, 'test_access_token')
        self.assertEqual(self.client.refresh_token, 'test_refresh_token')
        self.assertEqual(self.client.company_id, 'test_realm_id')
    
    @patch('quickbooks_client.requests.post')
    def test_exchange_code_for_tokens_failure(self, mock_post):
        """Test de intercambio fallido de código por tokens"""
        # Mock de respuesta de error
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = 'Bad Request'
        mock_post.return_value = mock_response
        
        result = self.client.exchange_code_for_tokens('invalid_code', 'test_realm_id')
        
        self.assertFalse(result)
        self.assertIsNone(self.client.access_token)
    
    @patch('quickbooks_client.requests.get')
    def test_make_api_request_success(self, mock_get):
        """Test de petición exitosa a la API"""
        # Configurar cliente con tokens
        self.client.access_token = 'test_access_token'
        self.client.company_id = 'test_company_id'
        
        # Mock de respuesta exitosa
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'QueryResponse': {
                'SalesReceipt': [{'Id': '1', 'TotalAmt': '100.00'}]
            }
        }
        mock_get.return_value = mock_response
        
        result = self.client.make_api_request('query', {'query': 'SELECT * FROM SalesReceipt'})
        
        self.assertIsNotNone(result)
        self.assertIn('QueryResponse', result)
    
    def test_make_api_request_no_tokens(self):
        """Test de petición sin tokens configurados"""
        result = self.client.make_api_request('query')
        self.assertIsNone(result)
    
    def test_get_monthly_sales_summary_format(self):
        """Test del formato del resumen mensual"""
        # Mock del cliente para simular datos
        with patch.object(self.client, 'get_sales_receipts') as mock_receipts, \
             patch.object(self.client, 'get_invoices') as mock_invoices:
            
            mock_receipts.return_value = [
                {'TotalAmt': '100.00'},
                {'TotalAmt': '200.00'}
            ]
            mock_invoices.return_value = [
                {'TotalAmt': '150.00'}
            ]
            
            summary = self.client.get_monthly_sales_summary()
            
            # Verificar estructura del resumen
            self.assertIn('período', summary)
            self.assertIn('fecha_inicio', summary)
            self.assertIn('fecha_fin', summary)
            self.assertIn('recibos_de_venta', summary)
            self.assertIn('facturas', summary)
            self.assertIn('total_ventas', summary)
            self.assertIn('detalle_transacciones', summary)
            
            # Verificar cálculos
            self.assertEqual(summary['recibos_de_venta']['cantidad'], 2)
            self.assertEqual(summary['recibos_de_venta']['total'], 300.0)
            self.assertEqual(summary['facturas']['cantidad'], 1)
            self.assertEqual(summary['facturas']['total'], 150.0)
            self.assertEqual(summary['total_ventas'], 450.0)

class TestEnvironmentVariables(unittest.TestCase):
    """Tests para verificar variables de entorno"""
    
    def test_required_env_vars_exist(self):
        """Test de que las variables de entorno requeridas estén definidas"""
        # Este test verifica que el archivo .env exista o que las variables estén configuradas
        required_vars = [
            'QB_CLIENT_ID',
            'QB_CLIENT_SECRET', 
            'QB_REDIRECT_URI'
        ]
        
        # Verificar que al menos el archivo de ejemplo exista
        self.assertTrue(
            os.path.exists('config.env.example') or 
            os.path.exists('.env') or
            all(os.getenv(var) for var in required_vars),
            "Debe existir config.env.example, .env, o las variables de entorno configuradas"
        )

def run_integration_test():
    """
    Test de integración que requiere credenciales reales
    Solo se ejecuta si las credenciales están configuradas
    """
    print("🧪 Ejecutando test de integración...")
    
    client = QuickBooksClient()
    
    if not client.client_id or client.client_id == 'tu_client_id_aqui':
        print("⚠️  Saltando test de integración: credenciales no configuradas")
        return
    
    print("✅ Credenciales configuradas")
    print(f"   Client ID: {client.client_id[:10]}...")
    
    # Test de URL de autorización
    auth_url = client.get_auth_url()
    print(f"✅ URL de autorización generada: {len(auth_url)} caracteres")
    
    # Si hubiera tokens válidos, se podrían probar más funciones
    print("ℹ️  Para tests completos, autoriza la aplicación primero")

if __name__ == '__main__':
    # Ejecutar tests unitarios
    print("🧪 Ejecutando tests unitarios...")
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "="*50)
    
    # Ejecutar test de integración
    run_integration_test()