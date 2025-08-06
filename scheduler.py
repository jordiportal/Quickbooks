"""
Scheduler para actualizaciones automáticas de ventas de QuickBooks
Utiliza APScheduler para ejecutar tareas en background
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from quickbooks_client import QuickBooksClient
from sales_cache import cache_service, SalesCacheService

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SalesUpdateScheduler:
    """Scheduler para actualizaciones automáticas de ventas"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.active_companies = {}  # company_id -> {access_token, refresh_token}
        self.update_interval_hours = int(os.getenv('SALES_UPDATE_INTERVAL', '1'))  # Default: cada hora
        self.cache_service = cache_service
        
        # Configurar jobs
        self._setup_jobs()
        
        logger.info(f"SalesUpdateScheduler iniciado - Intervalo: {self.update_interval_hours}h")
    
    def _setup_jobs(self):
        """Configurar todos los jobs del scheduler"""
        
        # Job principal: Actualizar ventas cada X horas
        self.scheduler.add_job(
            func=self._update_all_sales_job,
            trigger=IntervalTrigger(hours=self.update_interval_hours),
            id='update_sales',
            name='Actualizar ventas de todas las empresas',
            replace_existing=True,
            next_run_time=datetime.now() + timedelta(minutes=1)  # Primera ejecución en 1 minuto
        )
        
        # Job de limpieza: Limpiar cache antiguo diariamente a las 2 AM
        self.scheduler.add_job(
            func=self._cleanup_cache_job,
            trigger=CronTrigger(hour=2, minute=0),
            id='cleanup_cache',
            name='Limpiar cache antiguo',
            replace_existing=True
        )
        
        # Job de estadísticas: Log de estadísticas cada 6 horas
        self.scheduler.add_job(
            func=self._log_stats_job,
            trigger=IntervalTrigger(hours=6),
            id='log_stats',
            name='Log estadísticas del cache',
            replace_existing=True
        )
    
    def register_company(self, company_id: str, access_token: str, refresh_token: str = None):
        """
        Registrar una empresa para actualizaciones automáticas
        
        Args:
            company_id: ID de la empresa en QuickBooks
            access_token: Token de acceso OAuth
            refresh_token: Token de refresco OAuth (opcional)
        """
        self.active_companies[company_id] = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'registered_at': datetime.now().isoformat()
        }
        
        logger.info(f"📝 Empresa registrada para actualizaciones: {company_id}")
        
        # Ejecutar actualización inmediata para esta empresa
        self.scheduler.add_job(
            func=self._update_single_company,
            args=[company_id],
            id=f'immediate_update_{company_id}',
            name=f'Actualización inmediata: {company_id}',
            replace_existing=True,
            next_run_time=datetime.now() + timedelta(seconds=10)
        )
    
    def unregister_company(self, company_id: str):
        """Desregistrar empresa de actualizaciones automáticas"""
        if company_id in self.active_companies:
            del self.active_companies[company_id]
            logger.info(f"📝 Empresa desregistrada: {company_id}")
    
    def _update_single_company(self, company_id: str) -> bool:
        """
        Actualizar ventas de una empresa específica
        
        Args:
            company_id: ID de la empresa
            
        Returns:
            bool: True si la actualización fue exitosa
        """
        if company_id not in self.active_companies:
            logger.warning(f"⚠️  Empresa no registrada: {company_id}")
            return False
        
        company_data = self.active_companies[company_id]
        
        try:
            # Crear cliente QuickBooks con tokens
            qb_client = QuickBooksClient()
            qb_client.access_token = company_data['access_token']
            qb_client.refresh_token = company_data.get('refresh_token')
            qb_client.company_id = company_id
            
            # Obtener datos de ventas del mes actual
            sales_data = qb_client.get_monthly_sales_summary()
            
            # Actualizar cache
            success = self.cache_service.update_sales_cache(
                company_id=company_id,
                sales_data=sales_data,
                access_token=company_data['access_token'],
                refresh_token=company_data.get('refresh_token')
            )
            
            if success:
                logger.info(f"✅ Actualización exitosa: {company_id} - ${sales_data['total_ventas']:.2f}")
                
                # Si los tokens se renovaron, actualizar en memoria
                if qb_client.access_token != company_data['access_token']:
                    self.active_companies[company_id]['access_token'] = qb_client.access_token
                    if qb_client.refresh_token:
                        self.active_companies[company_id]['refresh_token'] = qb_client.refresh_token
                    logger.info(f"🔄 Tokens actualizados para: {company_id}")
                
                return True
            else:
                logger.error(f"❌ Error actualizando cache: {company_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error actualizando {company_id}: {str(e)}")
            
            # Si el error es de autenticación, desregistrar la empresa
            if 'unauthorized' in str(e).lower() or '401' in str(e):
                logger.warning(f"🔐 Tokens inválidos, desregistrando: {company_id}")
                self.unregister_company(company_id)
            
            return False
    
    def _update_all_sales_job(self):
        """Job principal: actualizar ventas de todas las empresas registradas"""
        logger.info(f"🔄 Iniciando actualización programada de ventas: {datetime.now()}")
        
        if not self.active_companies:
            logger.info("📭 No hay empresas registradas para actualización")
            return
        
        successful_updates = 0
        failed_updates = 0
        
        for company_id in list(self.active_companies.keys()):  # Lista para evitar modificación durante iteración
            try:
                if self._update_single_company(company_id):
                    successful_updates += 1
                else:
                    failed_updates += 1
            except Exception as e:
                logger.error(f"❌ Error inesperado actualizando {company_id}: {e}")
                failed_updates += 1
        
        logger.info(f"📊 Actualización completada: ✅{successful_updates} exitosas, ❌{failed_updates} fallidas")
    
    def _cleanup_cache_job(self):
        """Job de limpieza: eliminar entradas de cache antiguas"""
        logger.info("🧹 Iniciando limpieza de cache...")
        
        try:
            deleted_count = self.cache_service.cleanup_old_cache(days_to_keep=90)
            logger.info(f"🧹 Limpieza completada: {deleted_count} entradas eliminadas")
        except Exception as e:
            logger.error(f"❌ Error en limpieza de cache: {e}")
    
    def _log_stats_job(self):
        """Job de estadísticas: log periódico del estado del sistema"""
        try:
            stats = self.cache_service.get_cache_stats()
            logger.info(f"📈 Estadísticas del cache: {stats['total_entries']} entradas, "
                       f"{stats['successful_updates']} exitosas, {stats['failed_updates']} fallidas")
            logger.info(f"👥 Empresas activas: {len(self.active_companies)}")
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
    
    def start(self):
        """Iniciar el scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("🚀 Scheduler iniciado")
        else:
            logger.warning("⚠️  Scheduler ya está ejecutándose")
    
    def stop(self):
        """Detener el scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("🛑 Scheduler detenido")
    
    def get_jobs_status(self) -> Dict:
        """Obtener estado de todos los jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        
        return {
            'scheduler_running': self.scheduler.running,
            'active_companies': len(self.active_companies),
            'jobs': jobs,
            'companies': list(self.active_companies.keys())
        }
    
    def force_update(self, company_id: str = None) -> Dict:
        """
        Forzar actualización inmediata
        
        Args:
            company_id: ID específico de empresa (opcional, actualiza todas si no se especifica)
            
        Returns:
            Dict con resultados de la actualización
        """
        logger.info(f"🔄 Forzando actualización inmediata: {company_id or 'todas las empresas'}")
        
        if company_id:
            # Actualizar empresa específica
            if company_id in self.active_companies:
                success = self._update_single_company(company_id)
                return {
                    'company_id': company_id,
                    'success': success,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'company_id': company_id,
                    'success': False,
                    'error': 'Empresa no registrada',
                    'timestamp': datetime.now().isoformat()
                }
        else:
            # Actualizar todas las empresas
            self._update_all_sales_job()
            return {
                'action': 'update_all',
                'active_companies': len(self.active_companies),
                'timestamp': datetime.now().isoformat()
            }

# Instancia global del scheduler
sales_scheduler = SalesUpdateScheduler()