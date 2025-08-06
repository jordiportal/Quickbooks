"""
Servicio de Cache para ventas de QuickBooks Online
Maneja almacenamiento en SQLite y archivos JSON para detalles
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from quickbooks_client import QuickBooksClient

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

class SalesCache(Base):
    """Modelo para cache de resúmenes de ventas"""
    __tablename__ = 'sales_cache'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(String, nullable=False)
    period = Column(String, nullable=False)  # Formato: "MM/YYYY"
    total_sales = Column(Float, default=0.0)
    receipts_count = Column(Integer, default=0)
    receipts_total = Column(Float, default=0.0)
    invoices_count = Column(Integer, default=0)
    invoices_total = Column(Float, default=0.0)
    fecha_inicio = Column(String)  # YYYY-MM-DD
    fecha_fin = Column(String)     # YYYY-MM-DD
    last_updated = Column(DateTime, default=datetime.now)
    update_success = Column(String, default='true')  # 'true', 'false', 'error'
    error_message = Column(String, nullable=True)
    
    __table_args__ = (
        UniqueConstraint('company_id', 'period', name='_company_period_uc'),
    )
    
    def to_dict(self):
        """Convertir a diccionario para JSON"""
        return {
            'company_id': self.company_id,
            'período': self.period,
            'total_ventas': float(self.total_sales),
            'recibos_de_venta': {
                'cantidad': self.receipts_count,
                'total': float(self.receipts_total)
            },
            'facturas': {
                'cantidad': self.invoices_count,
                'total': float(self.invoices_total)
            },
            'fecha_inicio': self.fecha_inicio,
            'fecha_fin': self.fecha_fin,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'update_success': self.update_success == 'true',
            'error_message': self.error_message
        }

class SalesCacheService:
    """Servicio para manejar el cache de ventas"""
    
    def __init__(self, db_path: str = 'data/sales_cache.db'):
        self.db_path = db_path
        self.data_dir = os.path.dirname(db_path)
        
        # Crear directorio si no existe
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Configurar SQLAlchemy
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        logger.info(f"SalesCacheService iniciado con DB: {db_path}")
    
    def _get_details_file_path(self, company_id: str, period: str) -> str:
        """Generar ruta del archivo JSON de detalles"""
        # Convertir MM/YYYY a YYYY_MM para nombre de archivo
        try:
            month, year = period.split('/')
            filename = f"sales_details_{company_id}_{year}_{month:0>2}.json"
            return os.path.join(self.data_dir, filename)
        except:
            # Fallback si el formato no es el esperado
            safe_period = period.replace('/', '_')
            filename = f"sales_details_{company_id}_{safe_period}.json"
            return os.path.join(self.data_dir, filename)
    
    def _save_details_json(self, company_id: str, sales_data: Dict):
        """Guardar detalles completos en archivo JSON"""
        try:
            file_path = self._get_details_file_path(company_id, sales_data['período'])
            
            # Agregar timestamp de actualización
            sales_data_with_meta = {
                **sales_data,
                'cached_at': datetime.now().isoformat(),
                'cache_version': '1.0'
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(sales_data_with_meta, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Detalles guardados: {file_path}")
            
        except Exception as e:
            logger.error(f"Error guardando detalles JSON: {e}")
    
    def _load_details_json(self, company_id: str, period: str) -> Dict:
        """Cargar detalles desde archivo JSON"""
        try:
            file_path = self._get_details_file_path(company_id, period)
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
        except Exception as e:
            logger.error(f"Error cargando detalles JSON: {e}")
        
        return {}
    
    def update_sales_cache(self, company_id: str, sales_data: Dict, access_token: str = None, refresh_token: str = None) -> bool:
        """
        Actualizar cache con nuevos datos de ventas
        
        Args:
            company_id: ID de la empresa en QuickBooks
            sales_data: Datos de ventas del QuickBooksClient
            access_token: Token de acceso (opcional, para actualización automática)
            refresh_token: Token de refresco (opcional)
        
        Returns:
            bool: True si la actualización fue exitosa
        """
        session = self.Session()
        try:
            # Buscar entrada existente
            cache_entry = session.query(SalesCache).filter_by(
                company_id=company_id,
                period=sales_data['período']
            ).first()
            
            if not cache_entry:
                cache_entry = SalesCache(
                    company_id=company_id,
                    period=sales_data['período']
                )
                session.add(cache_entry)
                logger.info(f"Creando nueva entrada de cache: {company_id} - {sales_data['período']}")
            else:
                logger.info(f"Actualizando entrada existente: {company_id} - {sales_data['período']}")
            
            # Actualizar todos los campos
            cache_entry.total_sales = float(sales_data.get('total_ventas', 0))
            cache_entry.receipts_count = sales_data.get('recibos_de_venta', {}).get('cantidad', 0)
            cache_entry.receipts_total = float(sales_data.get('recibos_de_venta', {}).get('total', 0))
            cache_entry.invoices_count = sales_data.get('facturas', {}).get('cantidad', 0)
            cache_entry.invoices_total = float(sales_data.get('facturas', {}).get('total', 0))
            cache_entry.fecha_inicio = sales_data.get('fecha_inicio', '')
            cache_entry.fecha_fin = sales_data.get('fecha_fin', '')
            cache_entry.last_updated = datetime.now()
            cache_entry.update_success = 'true'
            cache_entry.error_message = None
            
            session.commit()
            
            # Guardar detalles completos en JSON
            self._save_details_json(company_id, sales_data)
            
            logger.info(f"✅ Cache actualizado: {company_id} - Total: ${cache_entry.total_sales:.2f}")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Error actualizando cache: {e}")
            
            # Intentar guardar el error en la base de datos
            try:
                if cache_entry:
                    cache_entry.update_success = 'error'
                    cache_entry.error_message = str(e)
                    cache_entry.last_updated = datetime.now()
                    session.commit()
            except:
                pass
            
            return False
            
        finally:
            session.close()
    
    def get_cached_sales(self, company_id: str, period: str = None) -> Optional[Dict]:
        """
        Obtener datos de ventas del cache
        
        Args:
            company_id: ID de la empresa
            period: Período en formato MM/YYYY (opcional, usa mes actual si no se especifica)
        
        Returns:
            Dict con datos de ventas o None si no se encuentra
        """
        if not period:
            period = datetime.now().strftime('%m/%Y')
        
        session = self.Session()
        try:
            cache_entry = session.query(SalesCache).filter_by(
                company_id=company_id,
                period=period
            ).first()
            
            if cache_entry:
                # Combinar datos del SQLite con detalles del JSON
                result = cache_entry.to_dict()
                
                # Cargar detalles completos del JSON
                details = self._load_details_json(company_id, period)
                if details.get('detalle_transacciones'):
                    result['detalle_transacciones'] = details['detalle_transacciones']
                
                logger.info(f"📊 Cache hit: {company_id} - {period}")
                return result
            
            logger.info(f"📊 Cache miss: {company_id} - {period}")
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo cache: {e}")
            return None
            
        finally:
            session.close()
    
    def get_all_cached_periods(self, company_id: str) -> List[Dict]:
        """Obtener todos los períodos en cache para una empresa"""
        session = self.Session()
        try:
            entries = session.query(SalesCache).filter_by(company_id=company_id).order_by(SalesCache.period.desc()).all()
            return [entry.to_dict() for entry in entries]
        finally:
            session.close()
    
    def cleanup_old_cache(self, days_to_keep: int = 90):
        """Limpiar entradas de cache más antiguas que X días"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        session = self.Session()
        try:
            deleted = session.query(SalesCache).filter(SalesCache.last_updated < cutoff_date).delete()
            session.commit()
            logger.info(f"🧹 Limpieza de cache: {deleted} entradas eliminadas")
            return deleted
        except Exception as e:
            session.rollback()
            logger.error(f"Error en limpieza de cache: {e}")
            return 0
        finally:
            session.close()
    
    def get_cache_stats(self) -> Dict:
        """Obtener estadísticas del cache"""
        session = self.Session()
        try:
            total_entries = session.query(SalesCache).count()
            successful_updates = session.query(SalesCache).filter_by(update_success='true').count()
            failed_updates = session.query(SalesCache).filter_by(update_success='error').count()
            
            latest_update = session.query(SalesCache).order_by(SalesCache.last_updated.desc()).first()
            oldest_entry = session.query(SalesCache).order_by(SalesCache.last_updated.asc()).first()
            
            return {
                'total_entries': total_entries,
                'successful_updates': successful_updates,
                'failed_updates': failed_updates,
                'latest_update': latest_update.last_updated.isoformat() if latest_update else None,
                'oldest_entry': oldest_entry.last_updated.isoformat() if oldest_entry else None,
                'cache_db_path': self.db_path,
                'data_directory': self.data_dir
            }
        finally:
            session.close()

# Instancia global del servicio de cache
cache_service = SalesCacheService()