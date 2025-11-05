import streamlit as st
import numpy as np
import pandas as pd
import math
import io
import re
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime
import asyncio
import concurrent.futures
from functools import lru_cache
import gc
import threading
from streamlit import components
import time

# Optional imports for performance monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
# Offline mode indicator
st.markdown('<div class="offline-indicator">📱 Offline Ready</div>', unsafe_allow_html=True)
# Custom CSS for better UI - MEJORADO
st.markdown("""
<style>
    /* TEMAS DE COLOR */
    :root {
        --primary-color: #2563eb;
        --secondary-color: #1e40af;
        --success-color: #059669;
        --warning-color: #d97706;
        --error-color: #dc2626;
        --background-light: #f8fafc;
        --background-dark: #0f172a;
        --text-light: #1e293b;
        --text-dark: #e2e8f0;
    }
    
    /* Responsive design mejorado */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem !important;
            padding: 0.5rem !important;
        }
        .stButton > button {
            width: 100% !important;
            margin: 0.25rem 0 !important;
        }
    }
    
    @media (max-width: 480px) {
        .main-header {
            font-size: 1.5rem !important;
        }
    }
   
    .main-header {
        font-size: 2.5rem;
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.2);
    }
   
    /* Plotly controls styling */
    .modebar {
        position: absolute !important;
        top: 50px !important;
        right: 15px !important;
        z-index: 1000 !important;
    }
   
    .modebar-btn {
        width: 32px !important;
        height: 32px !important;
        margin: 2px !important;
        border-radius: 6px !important;
        background-color: rgba(30, 30, 30, 0.95) !important;
        border: 1.5px solid #1f77b4 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
    }
   
    .modebar-btn svg path {
        fill: white !important;
    }
   
    .modebar-btn:hover {
        background-color: #1f77b4 !important;
        border-color: #4a9eff !important;
        transform: scale(1.08);
        transition: all 0.2s ease;
    }
   
    .modebar-group {
        background-color: rgba(30, 30, 30, 0.95) !important;
        padding: 4px !important;
        border-radius: 8px !important;
        margin: 3px !important;
        box-shadow: 0 3px 12px rgba(0,0,0,0.4) !important;
    }
   
    @media (max-width: 768px) {
        .modebar {
            top: 45px !important;
            right: 10px !important;
        }
        .modebar-btn {
            width: 38px !important;
            height: 38px !important;
        }
    }
   
    /* Estilos para botones de puntos */
    .point-button {
        background-color: #28a745 !important;
        color: white !important;
        border-color: #28a745 !important;
        border-radius: 8px !important;
    }
   
    .point-button:hover {
        background-color: #218838 !important;
        border-color: #1e7e34 !important;
    }
   
    .clear-points-button {
        background-color: #dc3545 !important;
        color: white !important;
        border-color: #dc3545 !important;
    }
   
    .clear-points-button:hover {
        background-color: #c82333 !important;
        border-color: #bd2130 !important;
    }
   
    /* Mover el gráfico hacia abajo */
    div[data-testid="stPlotlyChart"] {
        margin-top: 50px !important;
    }
   
    /* Desactivar pull-to-refresh en Android/Chrome */
    html, body, .stApp, div#root {
        overscroll-behavior-y: none !important;
        touch-action: pan-y !important;
    }
   
    /* Estilo para el indicador offline */
    .offline-indicator {
        position: fixed;
        top: 10px;
        right: 10px;
        background-color: #28a745;
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        z-index: 999;
    }

    /* Optimización para tabla en móvil */
    div[data-testid="stDataFrame"] {
        overflow-x: auto;
    }

    @media (max-width: 768px) {
        div[data-testid="stDataFrame"] {
            font-size: 12px;
        }
    }

    /* Plotly chart responsive optimizations */
    .js-plotly-plot .plotly {
        width: 100% !important;
        height: auto !important;
    }

    /* Mobile-specific plot adjustments */
    @media (max-width: 768px) {
        .js-plotly-plot .plotly {
            font-size: 12px !important;
        }
        
        .js-plotly-plot .plotly .legend {
            font-size: 10px !important;
        }
        
        .js-plotly-plot .plotly .xtitle,
        .js-plotly-plot .plotly .ytitle {
            font-size: 12px !important;
        }
        
        .js-plotly-plot .plotly .xtick,
        .js-plotly-plot .plotly .ytick {
            font-size: 9px !important;
        }
    }

    @media (max-width: 480px) {
        .js-plotly-plot .plotly {
            font-size: 10px !important;
        }
        
        .js-plotly-plot .plotly .legend {
            font-size: 8px !important;
        }
        
        .js-plotly-plot .plotly .xtitle,
        .js-plotly-plot .plotly .ytitle {
            font-size: 10px !important;
        }
        
        .js-plotly-plot .plotly .xtick,
        .js-plotly-plot .plotly .ytick {
            font-size: 8px !important;
        }
    }

    /* Mejoras para responsividad en portrait */
    @media (orientation: portrait) {
        div[data-testid="stPlotlyChart"] {
            height: 50vh !important;
            width: 100% !important;
        }
        .js-plotly-plot .plotly .modebar {
            top: 0 !important;
            right: 0 !important;
        }
        .js-plotly-plot .plotly {
            height: 50vh !important;
        }
        .stMarkdown, .stNumberInput, .stTextInput, .stButton {
            margin-bottom: 0.5rem !important;
            padding: 0.5rem !important;
        }
        .stExpander {
            margin-bottom: 0.5rem !important;
        }
        .stDataFrame {
            height: 200px !important;
        }
        .row-widget.stButton {
            margin-top: 0.5rem !important;
        }
        .stMetric {
            font-size: 14px !important;
        }
        h1, h2, h3, h4, h5, h6 {
            margin-top: 0.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        .stColumns > div {
            margin-bottom: 0.5rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)
# JavaScript to prevent pull-to-refresh
st.markdown("""
<script>
    document.addEventListener('touchstart', function(e) {
        if (window.scrollY === 0 && e.touches[0].clientY < 50) {
            e.preventDefault();
        }
    }, { passive: false });
   
    document.addEventListener('touchmove', function(e) {
        if (window.scrollY === 0 && e.touches[0].clientY < 50) {
            e.preventDefault();
        }
    }, { passive: false });
</script>
""", unsafe_allow_html=True)

# JavaScript for offline functionality and localStorage data persistence
st.markdown("""
<script>
    // Offline detection and service worker registration
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            // Register a simple service worker for offline functionality
            const sw = `
                self.addEventListener('install', function(event) {
                    event.waitUntil(
                        caches.open('azimuth-app-v1').then(function(cache) {
                            return cache.addAll([
                                '/',
                                '/app.py'
                            ]);
                        })
                    );
                });
                
                self.addEventListener('fetch', function(event) {
                    event.respondWith(
                        caches.match(event.request).then(function(response) {
                            return response || fetch(event.request);
                        })
                    );
                });
            `;
            
            const blob = new Blob([sw], { type: 'application/javascript' });
            const swUrl = URL.createObjectURL(blob);
            
            navigator.serviceWorker.register(swUrl).then(function(registration) {
                console.log('ServiceWorker registrado para offline');
            }).catch(function(error) {
                console.log('ServiceWorker registration failed:', error);
            });
        });
    }
    
    // Network status detection
    function updateNetworkStatus() {
        const statusElement = document.querySelector('.offline-indicator');
        if (navigator.onLine) {
            if (statusElement) {
                statusElement.textContent = '📱 Online';
                statusElement.style.backgroundColor = '#28a745';
            }
        } else {
            if (statusElement) {
                statusElement.textContent = '📱 Offline Mode';
                statusElement.style.backgroundColor = '#dc3545';
            }
        }
    }
    
    // Listen for network status changes
    window.addEventListener('online', updateNetworkStatus);
    window.addEventListener('offline', updateNetworkStatus);
    
    // Update status on load
    document.addEventListener('DOMContentLoaded', updateNetworkStatus);
    
    // Enhanced localStorage with error handling and backup
    function saveAzimuthData(batchData, singlePoints, referencePoint) {
        try {
            const data = {
                batch_data: batchData || [],
                single_points: singlePoints || [],
                reference_point: referencePoint || {x: 1000, y: 1000},
                timestamp: new Date().toISOString(),
                version: '1.0'
            };
            
            // Save to localStorage with backup
            localStorage.setItem('azimuthAppData', JSON.stringify(data));
            localStorage.setItem('azimuthAppData_backup', JSON.stringify(data));
            
            console.log('Datos guardados exitosamente (offline ready)');
            return true;
        } catch (e) {
            console.log('Error saving data:', e);
            return false;
        }
    }
    
    // Load data from localStorage with fallback
    function loadAzimuthData() {
        try {
            let saved = localStorage.getItem('azimuthAppData');
            
            // If main data not found, try backup
            if (!saved) {
                saved = localStorage.getItem('azimuthAppData_backup');
            }
            
            if (saved) {
                const data = JSON.parse(saved);
                console.log('Datos cargados exitosamente (offline ready)');
                return data;
            }
        } catch (e) {
            console.log('Error loading data:', e);
        }
        return null;
    }
    
    // Clear saved data
    function clearAzimuthData() {
        try {
            localStorage.removeItem('azimuthAppData');
            localStorage.removeItem('azimuthAppData_backup');
            console.log('Datos limpiados exitosamente');
            return true;
        } catch (e) {
            console.log('Error clearing data:', e);
            return false;
        }
    }
    
    // Check available storage
    function checkStorageSpace() {
        try {
            const estimate = navigator.storage && navigator.storage.estimate;
            if (estimate) {
                estimate().then(function(quota) {
                    const usage = quota.usage || 0;
                    const quota_available = quota.quota || 0;
                    const percentage = (usage / quota_available * 100).toFixed(2);
                    console.log('Storage usage:', percentage + '%');
                });
            }
        } catch (e) {
            console.log('Storage check failed:', e);
        }
    }
    
    // Auto-save functionality
    window.saveAzimuthData = saveAzimuthData;
    window.loadAzimuthData = loadAzimuthData;
    window.clearAzimuthData = clearAzimuthData;
    window.checkStorageSpace = checkStorageSpace;
    
    // Check storage on load
    checkStorageSpace();
</script>
""", unsafe_allow_html=True)
# Language translations (solo español)
TRANSLATIONS = {
    'es': {
        'title': '🧭 Convertidor de Azimut a Coordenadas',
        'subtitle': 'Convierte medidas de azimut y distancia a coordenadas X,Y o ingresa puntos directamente.',
        'settings': '⚙️ Configuración',
        'language': '🌍 Idioma',
        'reference_point': 'Punto de Referencia',
        'reference_x': 'Referencia X',
        'reference_y': 'Referencia Y',
        'reference_x_help': 'Coordenada X del punto de referencia',
        'reference_y_help': 'Coordenada Y del punto de referencia',
        'batch_conversion': '📊 Conversión por Lotes',
        'azimuth_input_format': 'Formato de Entrada de Azimut',
        'dms_format': 'GMS (266°56\'7.24")',
        'decimal_format': 'Decimal (266.935)',
        'azimuth_easy_input': 'Azimut (Entrada Fácil Móvil)',
        'azimuth_placeholder': 'Formatos fáciles: 26 56 7.00 o 26-56-7.00 o 26:56:7.00',
        'azimuth_help': 'Formatos amigables para móvil:\n• Espacios: 26 56 7.00\n• Guiones: 26-56-7.00\n• Dos puntos: 26:56:7.00\n• Tradicional: 26°56\'7.00"',
        'azimuth_decimal': 'Azimut (grados decimales)',
        'azimuth_decimal_help': 'Ingresa el ángulo de azimut en grados decimales (0-360)',
        'distance': 'Distancia',
        'distance_help': 'Ingresa la distancia desde el punto de referencia',
        'results': '📍 Resultados',
        'x_coordinate': 'Coordenada X',
        'y_coordinate': 'Coordenada Y',
        'x_input': 'Coordenada X',
        'y_input': 'Coordenada Y',
        'x_input_help': 'Ingresa la coordenada X del punto',
        'y_input_help': 'Ingresa la coordenada Y del punto',
        'input_summary': 'Entrada:',
        'enter_values': '👈 Ingresa valores de coordenadas para ver resultados',
        'calculation_error': '❌ Error de Cálculo:',
        'parsed_success': '✅ Analizado:',
        'parse_error': '❌ No se pudo analizar',
        'try_format': 'Intenta formato como: 45°30\'15" o 120°0\'0\'\'',
        'azimuth_warning': '⚠️ Azimut {:.3f}° está fuera del rango 0-360°',
        'visualization': '📈 Visualización',
    }
}
# 🚀 PERFORMANCE: Smart Caching & Memory Management
class PerformanceManager:
    """Gestión inteligente de caché y memoria"""
    
    def __init__(self):
        self._cache_stats = {}
        self._memory_threshold = 100 * 1024 * 1024  # 100MB threshold
        self._cache_lock = threading.Lock()
    
    def optimize_memory(self):
        """Optimizar uso de memoria"""
        if gc.isenabled():
            gc.collect()
        
        # Limpiar cachés grandes si es necesario
        if self._should_clear_cache():
            with self._cache_lock:
                st.cache_data.clear()
                self._cache_stats.clear()
    
    def _should_clear_cache(self):
        """Determinar si se debe limpiar el caché"""
        # Implementar lógica basada en uso de memoria
        if PSUTIL_AVAILABLE and psutil is not None:
            memory_info = psutil.virtual_memory()
            return memory_info.percent > 80  # Limpiar si uso > 80%
        else:
            # Fallback simple: limpiar cada 50 operaciones
            return len(self._cache_stats) > 50
    
    def get_cache_stats(self):
        """Obtener estadísticas de caché"""
        return {
            'cache_hits': len(self._cache_stats),
            'memory_usage': self._get_memory_usage()
        }
    
    def _get_memory_usage(self):
        """Obtener uso de memoria actual"""
        if PSUTIL_AVAILABLE and psutil is not None:
            return psutil.Process().memory_info().rss / 1024 / 1024  # MB
        else:
            # Fallback: estimar uso basado en operaciones
            return len(self._cache_stats) * 0.5  # Estimación simple

# Instancia global del gestor de rendimiento
perf_manager = PerformanceManager()

# 🚀 PERFORMANCE: Async Processing Pool
class AsyncProcessor:
    """Procesamiento asíncrono para operaciones pesadas"""
    
    def __init__(self, max_workers=None):
        self.max_workers = max_workers or min(32, (threading.cpu_count() or 1) + 4)
        self._executor = None
        self._loop = None
    
    def __enter__(self):
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        self._loop = asyncio.new_event_loop()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._executor:
            self._executor.shutdown(wait=True)
        if self._loop:
            self._loop.close()
    
    async def process_batch_async(self, batch_data, ref_x, ref_y, azimuth_convention):
        """Procesar lote de coordenadas de forma asíncrona"""
        tasks = []
        
        for index, row in batch_data.iterrows():
            task = self._loop.run_in_executor(
                self._executor,
                self._process_single_point,
                row, ref_x, ref_y, azimuth_convention
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrar resultados válidos
        valid_results = [r for r in results if not isinstance(r, Exception)]
        return pd.DataFrame(valid_results)
    
    def _process_single_point(self, row, ref_x, ref_y, azimuth_convention):
        """Procesar punto individual"""
        try:
            azimuth = parse_dms_to_decimal(str(row['Azimuth']))
            if azimuth is None:
                return None
                
            distance = float(row['Distance'])
            x, y = azimuth_to_coordinates(azimuth, distance, ref_x, ref_y, azimuth_convention)
            
            return {
                'Row': row.name + 1,
                'X': x,
                'Y': y
            }
        except Exception:
            return None

# 🚀 PERFORMANCE: LRU Cache para funciones críticas
@lru_cache(maxsize=128)
def cached_parse_dms_to_decimal(dms_string):
    """Versión cacheada de parse_dms_to_decimal"""
    return parse_dms_to_decimal(dms_string)

@lru_cache(maxsize=256)
def cached_azimuth_to_coordinates(azimuth, distance, ref_x, ref_y, azimuth_convention):
    """Versión cacheada de azimuth_to_coordinates"""
    return azimuth_to_coordinates(azimuth, distance, ref_x, ref_y, azimuth_convention)

def get_text(key, lang='es'):
    """Get translated text for the given key and language"""
    return TRANSLATIONS['es'].get(key, key)
@st.cache_data(show_spinner=False, ttl=3600)  # Cache por 1 hora
def calculate_polygon_area(coordinates):
    """Calculate polygon area using the Shoelace formula - OPTIMIZADO"""
    if len(coordinates) < 3:
        return 0.0
    
    # Convertir a numpy array para mejor rendimiento
    coords = np.array(coordinates, dtype=np.float64)
    n = len(coords)
    
    # Usar vectorización de numpy para cálculo más rápido
    i = np.arange(n)
    j = (i + 1) % n
    
    # Optimización con operaciones vectorizadas
    area = np.sum(coords[i, 0] * coords[j, 1]) - np.sum(coords[i, 1] * coords[j, 0])
    
    # Liberar memoria temporal
    del coords, i, j
    
    return abs(area) / 2.0

@st.cache_data(show_spinner=False, ttl=3600)  # Cache por 1 hora
def batch_calculate_coordinates(batch_data, ref_x, ref_y, azimuth_convention):
    """Procesar lotes de cálculos con caché - MEJORADO CON PERFORMANCE"""
    
    # 🚀 PERFORMANCE: Optimización de memoria
    perf_manager.optimize_memory()
    
    # 🚀 PERFORMANCE: Procesamiento asíncrono para lotes grandes
    if len(batch_data) > 100:  # Usar async para lotes grandes
        try:
            with AsyncProcessor() as processor:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results_df = loop.run_until_complete(
                    processor.process_batch_async(batch_data, ref_x, ref_y, azimuth_convention)
                )
                loop.close()
                return results_df
        except Exception:
            # Fallback a procesamiento síncrono
            pass
    
    # 🚀 PERFORMANCE: Procesamiento vectorizado para lotes pequeños/medianos
    results = []
    current_ref_x, current_ref_y = ref_x, ref_y
    
    # Pre-allocar memoria para mejor rendimiento
    results = [None] * len(batch_data)
    valid_count = 0
    
    for index, row in batch_data.iterrows():
        try:
            # Usar versión cacheada para mejor rendimiento
            azimuth = cached_parse_dms_to_decimal(str(row['Azimuth']))
            if azimuth is None:
                continue
                
            distance = float(row['Distance'])
            
            # Usar versión cacheada de cálculo de coordenadas
            x, y = cached_azimuth_to_coordinates(
                azimuth, distance, current_ref_x, current_ref_y, azimuth_convention
            )
            
            results[valid_count] = {
                'Row': index + 1,
                'X': x,
                'Y': y
            }
            valid_count += 1
            
            current_ref_x, current_ref_y = x, y
            
        except Exception:
            continue
    
    # Crear DataFrame solo con resultados válidos
    final_results = results[:valid_count]
    
    # Liberar memoria temporal
    del results
    perf_manager.optimize_memory()
    
    return pd.DataFrame(final_results)
def azimuth_to_coordinates(azimuth, distance, ref_x=0.0, ref_y=0.0, azimuth_convention="north"):
    """Convert azimuth and distance to X,Y coordinates using Excel formulas - MEJORADO"""
    
    # Validación de entrada mejorada
    if not isinstance(azimuth, (int, float)) or not isinstance(distance, (int, float)):
        raise ValueError("Azimuth y distancia deben ser números")
    
    if distance < 0:
        raise ValueError("La distancia no puede ser negativa")
    
    # Normalizar azimuth al rango 0-360 grados
    azimuth = azimuth % 360
    
    # Manejo de casos especiales para distancias muy pequeñas
    if distance < 1e-10:
        return round(ref_x, 6), round(ref_y, 6)
    
    azimuth_rad = math.radians(azimuth)
    
    # Cálculo con precisión mejorada
    x_offset = math.sin(azimuth_rad) * distance
    y_offset = distance * math.cos(azimuth_rad)
    
    x = ref_x + x_offset
    y = ref_y + y_offset
    
    # Redondeo adaptativo basado en la magnitud
    if abs(x) > 1000 or abs(y) > 1000:
        precision = 3
    else:
        precision = 6
    
    return round(x, precision), round(y, precision)
def parse_dms_to_decimal(dms_string):
    """Convert degrees-minutes-seconds format to decimal degrees"""
    try:
        dms_string = str(dms_string).strip()
        dms_string = dms_string.replace(',', '.')
       
        patterns = [
            r'(\d+(?:\.\d+)?)[°d]\s*(\d+(?:\.\d+)?)[\'m]\s*(\d+(?:\.\d+)?)[\"\'s]?',
            r'^(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)$',
            r'^(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)$',
            r'^(\d+(?:\.\d+)?):(\d+(?:\.\d+)?):(\d+(?:\.\d+)?)$',
            r'^(\d+(?:\.\d+)?)_(\d+(?:\.\d+)?)_(\d+(?:\.\d+)?)$'
        ]
       
        for pattern in patterns:
            match = re.search(pattern, dms_string)
            if match and len(match.groups()) == 3:
                degrees = float(match.group(1))
                minutes = float(match.group(2))
                seconds = float(match.group(3))
                decimal_degrees = (((seconds / 60.0) + minutes) / 60.0) + degrees
                return decimal_degrees
       
        return float(dms_string.replace(',', '.'))
    except (ValueError, AttributeError):
        return None
def validate_azimuth(azimuth):
    """Validate azimuth value is within 0-360 degrees"""
    return 0 <= azimuth <= 360
@st.cache_data(show_spinner=False, ttl=1800)  # Cache por 30 minutos
def create_multi_point_plot(single_points, results_df, ref_x, ref_y, x_coord, y_coord, lang='es', bg_color='Blanco'):
    """Create interactive plot for multiple points and polygon - OPTIMIZADO"""
    
    # 🚀 PERFORMANCE: Optimización de memoria antes de crear el gráfico
    perf_manager.optimize_memory()
    
    fig = go.Figure()
   
    # Reference point
    ref_text_color = 'blue' if bg_color == 'Blanco' else 'lightblue'
    fig.add_trace(go.Scatter(
        x=[ref_x],
        y=[ref_y],
        mode='markers+text',
        name='Referencia',
        marker=dict(color='blue', size=16, symbol='circle'),
        text=['REF'],
        textposition='bottom center',
        textfont=dict(size=14, color=ref_text_color),
        hovertemplate='<b>Referencia</b><br>X: %{x:.3f}<br>Y: %{y:.3f}<extra></extra>'
    ))
   
    # Directly entered points (from single_points)
    single_points_area = 0.0 # Initialize area for single points polygon
    if not single_points.empty:
        colors = ['red', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        if bg_color == 'Negro':
            colors = ['lightcoral', 'gold', 'violet', 'sienna', 'lightpink', 'lightgray', 'lightgreen', 'lightcyan']
       
        # Plot individual points
        for i, (_, row) in enumerate(single_points.iterrows()):
            color = colors[i % len(colors)]
            point_name = f'P{i+1}'
           
            fig.add_trace(go.Scatter(
                x=[row['X']],
                y=[row['Y']],
                mode='markers+text',
                name=point_name,
                marker=dict(color=color, size=12, symbol='diamond'),
                text=[point_name],
                textposition='top center',
                textfont=dict(size=12, color=color),
                hovertemplate=f'<b>{point_name} (Ingresado)</b><br>X: %{{x:.3f}}<br>Y: %{{y:.3f}}<extra></extra>'
            ))
       
        # Add polygon connecting single points if there are at least 3 points
        if len(single_points) >= 3:
            all_x = single_points['X'].tolist()
            all_y = single_points['Y'].tolist()
           
            # Close the polygon by adding the first point at the end
            all_x.append(all_x[0])
            all_y.append(all_y[0])
           
            poly_line_color = 'green' if bg_color == 'Blanco' else 'lightgreen'
            fig.add_trace(go.Scatter(
                x=all_x,
                y=all_y,
                mode='lines',
                name='Polígono (Puntos Ingresados)',
                line=dict(color=poly_line_color, width=3),
                fill='toself',
                fillcolor='rgba(40, 167, 69, 0.2)', # Light green fill
                hoverinfo='skip'
            ))
           
            # Calculate area for single points polygon
            coordinates = list(zip(single_points['X'], single_points['Y']))
            single_points_area = calculate_polygon_area(coordinates)
   
    # Current preview point (if entered)
    if x_coord != 0 or y_coord != 0:
        preview_color = 'green' if bg_color == 'Blanco' else 'lightgreen'
        fig.add_trace(go.Scatter(
            x=[x_coord],
            y=[y_coord],
            mode='markers',
            name='Punto Actual (Vista Previa)',
            marker=dict(color=preview_color, size=14, symbol='x'),
            hovertemplate='<b>Punto Actual</b><br>X: %{x:.3f}<br>Y: %{y:.3f}<extra></extra>'
        ))
   
    # Polygon points (from results_df)
    polygon_area = 0.0 # Initialize area for azimuth-based polygon
    if not results_df.empty:
        all_x = [ref_x] + results_df['X_Coordinate'].tolist()
        all_y = [ref_y] + results_df['Y_Coordinate'].tolist()
       
        # Polygon trace
        poly_az_line_color = 'blue' if bg_color == 'Blanco' else 'lightblue'
        fig.add_trace(go.Scatter(
            x=all_x + [all_x[0]],
            y=all_y + [all_y[0]],
            mode='lines',
            name='Polígono (Azimut)',
            line=dict(color=poly_az_line_color, width=3),
            fill='toself',
            fillcolor='rgba(31, 119, 180, 0.2)',
            hoverinfo='skip'
        ))
       
        # Polygon points
        marker_color = 'red' if bg_color == 'Blanco' else 'lightcoral'
        text_color = 'black' if bg_color == 'Blanco' else 'white'
        if len(results_df) <= 20:
            labels = [f'A{i+1}' for i in range(len(results_df))]
            mode = 'markers+text'
        else:
            labels = None
            mode = 'markers'
       
        fig.add_trace(go.Scatter(
            x=results_df['X_Coordinate'],
            y=results_df['Y_Coordinate'],
            mode=mode,
            name='Puntos del Polígono (Azimut)',
            marker=dict(color=marker_color, size=10, symbol='circle'),
            text=labels,
            textposition='top center',
            textfont=dict(size=9, color=text_color),
            hovertemplate='<b>Punto A%{pointNumber}</b><br>X: %{x:.3f}<br>Y: %{y:.3f}<extra></extra>'
        ))
       
        # Arrows for polygon direction (optimized for mobile)
        arrow_color = 'rgba(0,100,200,0.5)' if bg_color == 'Blanco' else 'rgba(173,216,230,0.5)'
        annotation_font_color = 'darkblue' if bg_color == 'Blanco' else 'lightblue'
        
        # Only show arrows for small datasets on mobile
        show_arrows = len(results_df) <= 10  # Limit arrows on mobile
        
        if show_arrows:
            for i, row in results_df.iterrows():
                if i == 0:
                    start_x, start_y = ref_x, ref_y
                else:
                    start_x = results_df.iloc[i-1]['X_Coordinate']
                    start_y = results_df.iloc[i-1]['Y_Coordinate']
               
                fig.add_annotation(
                    x=row['X_Coordinate'],
                    y=row['Y_Coordinate'],
                    ax=start_x,
                    ay=start_y,
                    xref="x",
                    yref="y",
                    axref="x",
                    ayref="y",
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=0.8,  # Smaller arrows for mobile
                    arrowwidth=1,
                    arrowcolor=arrow_color,
                    text="",
                    font=dict(size=10, color=annotation_font_color),  # Smaller font
                    bgcolor='rgba(0,0,0,0)',
                    borderpad=0,
                    standoff=3  # Reduced standoff for mobile
                )
       
        # Calculate polygon area
        coordinates = [(ref_x, ref_y)] + list(zip(results_df['X_Coordinate'], results_df['Y_Coordinate']))
        polygon_area = calculate_polygon_area(coordinates)
   
    # Update layout
    title_text = (f'Visualización Combinada | Puntos Ingresados: {len(single_points)} '
                  f'| Área Puntos: {single_points_area:.3f} m² '
                  f'| Puntos Polígono Azimut: {len(results_df)} '
                  f'| Área Azimut: {polygon_area:.3f} m²')
    plot_bgcolor = 'white' if bg_color == 'Blanco' else 'black'
    grid_color = 'rgba(200,200,200,0.5)' if bg_color == 'Blanco' else 'rgba(100,100,100,0.5)'
    font_color = 'black' if bg_color == 'Blanco' else 'white'
    fig.update_layout(
        title={
            'text': title_text,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16, 'color': font_color}  # Smaller title for mobile
        },
        xaxis_title='X (m)',
        yaxis_title='Y (m)',
        showlegend=True,
        legend=dict(
            orientation="h",  # Horizontal legend for mobile
            yanchor="bottom",
            y=-0.15,  # Position below plot
            xanchor="center",
            x=0.5,
            font=dict(color=font_color, size=10)  # Smaller legend text
        ),
        hovermode='closest',
        height=600,  # Reduced height for mobile
        width=None,  # Auto-width for responsiveness
        margin=dict(l=50, r=20, t=80, b=100),  # Better margins for mobile
        yaxis=dict(scaleanchor="x", scaleratio=1),
        plot_bgcolor=plot_bgcolor,
        paper_bgcolor=plot_bgcolor,
        dragmode='pan',
        font=dict(color=font_color, size=12),  # Base font size
        autosize=True,  # Enable responsive sizing
        # Mobile-optimized modebar
        modebar=dict(
            orientation='h',
            bgcolor='rgba(255,255,255,0.7)',
            color='#333',
            activecolor='#1f77b4'
        )
    )
   
    fig.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor=grid_color, 
        title_font=dict(color=font_color, size=12), 
        tickfont=dict(color=font_color, size=10),  # Smaller ticks
        tickangle=0,  # Horizontal ticks
        automargin=True  # Auto margin for labels
    )
    fig.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor=grid_color, 
        title_font=dict(color=font_color, size=12), 
        tickfont=dict(color=font_color, size=10),  # Smaller ticks
        automargin=True  # Auto margin for labels
    )
   
    config = {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonSize': 14,  # Smaller buttons for mobile
        'doubleClick': 'reset',
        'scrollZoom': True,
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'combined_plot',
            'height': 800,  # Smaller export size
            'width': 1200,
            'scale': 1.5
        },
        # Mobile-specific options
        'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'eraseshape'],
        'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'autoScale2d'],
        'locale': 'es'  # Spanish locale
    }
   
    return fig, config

def export_to_dxf(coordinates, filename="coordinates.dxf"):
    """Exportar coordenadas a formato DXF para AutoCAD"""
    dxf_content = f"""0
SECTION
2
HEADER
9
$ACADVER
1
AC1015
0
ENDSEC
0
SECTION
2
ENTITIES
"""
    
    # Agregar puntos
    for i, (x, y) in enumerate(coordinates):
        dxf_content += f"""0
POINT
8
0
10
{x}
20
{y}
30
0.0
"""
    
    # Agregar líneas conectando los puntos
    if len(coordinates) > 1:
        for i in range(len(coordinates)):
            x1, y1 = coordinates[i]
            x2, y2 = coordinates[(i + 1) % len(coordinates)]
            dxf_content += f"""0
LINE
8
1
10
{x1}
20
{y1}
30
0.0
11
{x2}
21
{y2}
31
0.0
"""
    
    dxf_content += """0
ENDSEC
0
EOF
"""
    
    return dxf_content

def export_to_json(data, metadata=None):
    """Exportar datos a formato JSON con metadatos"""
    export_data = {
        "metadata": metadata or {
            "created_at": datetime.now().isoformat(),
            "version": "2.0",
            "software": "Azimuth Converter"
        },
        "data": data.to_dict('records') if hasattr(data, 'to_dict') else data
    }
    
    return json.dumps(export_data, indent=2, ensure_ascii=False)

def export_to_kml(coordinates, name="Survey Points"):
    """Exportar coordenadas a formato KML para Google Earth"""
    kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
<name>{name}</name>
"""
    
    for i, (x, y) in enumerate(coordinates):
        kml_content += f"""<Placemark>
<name>Point {i+1}</name>
<Point>
<coordinates>{x},{y},0</coordinates>
</Point>
</Placemark>
"""
    
    kml_content += """</Document>
</kml>"""
    
    return kml_content
# CONSTANTES Y CONFIGURACIONES
CLOSURE_TOLERANCE = 0.01
MAX_AZIMUTH_POINTS = 20
PLOT_HEIGHT = 1000
PLOT_WIDTH = 1600
MAX_COORDINATE_VALUE = 1e6

# CONFIGURACIÓN DE LA APLICACIÓN
APP_CONFIG = {
    'page_title': "Azimuth Converter",
    'page_icon': "🧭",
    'layout': "wide",
    'initial_sidebar_state': "auto"
}

def initialize_session_state():
    """Inicializar todas las variables de sesión"""
    if 'language' not in st.session_state:
        st.session_state.language = 'es'
    
    if 'single_points' not in st.session_state:
        st.session_state.single_points = pd.DataFrame({'X': [], 'Y': []})
    
    if 'batch_data' not in st.session_state:
        st.session_state.batch_data = pd.DataFrame({'Azimuth': [], 'Distance': []})
    
    if 'results_df' not in st.session_state:
        st.session_state.results_df = pd.DataFrame()

def save_data_to_local_storage():
    """Guardar datos en el almacenamiento local del navegador - MEJORADO PARA OFFLINE"""
    try:
        # Convertir DataFrames a listas de diccionarios
        batch_data_list = st.session_state.batch_data.to_dict('records') if not st.session_state.batch_data.empty else []
        single_points_list = st.session_state.single_points.to_dict('records') if not st.session_state.single_points.empty else []
        
        # Crear objeto de datos con versión y validación
        data = {
            'batch_data': batch_data_list,
            'single_points': single_points_list,
            'reference_point': {
                'x': st.session_state.get('ref_x', 1000.0),
                'y': st.session_state.get('ref_y', 1000.0)
            },
            'timestamp': datetime.now().isoformat(),
            'version': '1.0',
            'app_name': 'azimuth_converter'
        }
        
        # Validar datos antes de guardar
        if not isinstance(batch_data_list, list) or not isinstance(single_points_list, list):
            raise ValueError("Datos inválidos para guardar")
        
        # Guardar en el almacenamiento de sesión
        st.session_state['saved_data'] = json.dumps(data)
        
        # Llamar a JavaScript para guardar en localStorage con manejo de errores
        save_script = f"""
        <script>
            (function() {{
                try {{
                    const result = window.parent.saveAzimuthData(
                        {json.dumps(batch_data_list)}, 
                        {json.dumps(single_points_list)}, 
                        {json.dumps({'x': st.session_state.get('ref_x', 1000.0), 'y': st.session_state.get('ref_y', 1000.0)})}
                    );
                    console.log('Auto-guardado exitoso:', new Date().toLocaleTimeString());
                }} catch (e) {{
                    console.error('Error en auto-guardado:', e);
                }}
            }})();
        </script>
        """
        
        st.components.v1.html(save_script, height=0)
        
        # Actualizar estado de último guardado
        st.session_state['last_saved'] = datetime.now()
        
        # Mostrar confirmación breve en modo offline
        if not hasattr(st.session_state, 'save_notification_shown') or not st.session_state.save_notification_shown:
            show_toast("💾 Datos guardados localmente", "success", 2000)
            st.session_state.save_notification_shown = True
        
    except Exception as e:
        st.error(f"Error al guardar datos: {str(e)}")
        # Intentar guardar solo en session_state como fallback
        try:
            st.session_state['saved_data'] = json.dumps({
                'batch_data': [],
                'single_points': [],
                'reference_point': {'x': 1000, 'y': 1000},
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            })
        except:
            pass

def load_data_from_local_storage():
    """Cargar datos desde el almacenamiento local del navegador - MEJORADO PARA OFFLINE"""
    try:
        # Intentar cargar desde session_state primero (más rápido)
        if 'saved_data' in st.session_state:
            try:
                parsed = json.loads(st.session_state['saved_data'])
                if isinstance(parsed, dict) and 'app_name' in parsed:
                    # Datos válidos encontrados en session_state
                    st.session_state.loaded_azimuth_data = parsed
                    
                    # Actualizar DataFrames con datos cargados
                    if parsed.get('batch_data'):
                        st.session_state.batch_data = pd.DataFrame(parsed['batch_data'])
                    else:
                        st.session_state.batch_data = pd.DataFrame({'Azimuth': [], 'Distance': []})

                    if parsed.get('single_points'):
                        st.session_state.single_points = pd.DataFrame(parsed['single_points'])
                    else:
                        st.session_state.single_points = pd.DataFrame({'X': [], 'Y': []})

                    if parsed.get('reference_point'):
                        st.session_state.ref_x = parsed['reference_point'].get('x', st.session_state.get('ref_x', 1000.0))
                        st.session_state.ref_y = parsed['reference_point'].get('y', st.session_state.get('ref_y', 1000.0))

                    st.session_state.data_loaded = True
                    show_toast("📂 Datos cargados desde memoria", "info", 2000)
                    return True
            except Exception:
                pass  # Continuar con localStorage

        # Ejecutar JavaScript para cargar desde localStorage
        data = st.components.v1.html("""
        <script>
            (function() {
                try {
                    // Intentar cargar desde localStorage con fallback a backup
                    let savedData = localStorage.getItem('azimuthAppData');
                    if (!savedData) {
                        savedData = localStorage.getItem('azimuthAppData_backup');
                    }
                    
                    const value = savedData ? JSON.parse(savedData) : null;
                    
                    // Validar que los datos sean del app correcto
                    if (value && value.app_name === 'azimuth_converter') {
                        window.parent.postMessage({
                            type: 'streamlit:setComponentValue',
                            value: value
                        }, '*');
                        console.log('Datos válidos encontrados en localStorage');
                    } else {
                        window.parent.postMessage({
                            type: 'streamlit:setComponentValue',
                            value: null
                        }, '*');
                    }
                } catch (e) {
                    console.error('Error al cargar datos guardados:', e);
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        value: null
                    }, '*');
                }
            })();
        </script>
        """, height=0)
        
        # Procesar datos retornados
        parsed = None
        if isinstance(data, dict):
            parsed = data
        elif isinstance(data, str):
            try:
                parsed = json.loads(data)
            except Exception:
                parsed = None

        # Si logramos obtener datos válidos, actualizamos el estado
        if isinstance(parsed, dict) and 'app_name' in parsed:
            st.session_state.loaded_azimuth_data = parsed
            st.session_state['saved_data'] = json.dumps(parsed)  # Guardar en session_state también

            # Actualizar DataFrames con datos cargados
            if parsed.get('batch_data'):
                st.session_state.batch_data = pd.DataFrame(parsed['batch_data'])
            else:
                st.session_state.batch_data = pd.DataFrame({'Azimuth': [], 'Distance': []})

            if parsed.get('single_points'):
                st.session_state.single_points = pd.DataFrame(parsed['single_points'])
            else:
                st.session_state.single_points = pd.DataFrame({'X': [], 'Y': []})

            if parsed.get('reference_point'):
                st.session_state.ref_x = parsed['reference_point'].get('x', st.session_state.get('ref_x', 1000.0))
                st.session_state.ref_y = parsed['reference_point'].get('y', st.session_state.get('ref_y', 1000.0))

            st.session_state.data_loaded = True
            show_toast("📂 Datos cargados desde almacenamiento local", "info", 2000)
            return True

        # Si no hay datos
        st.info("📭 No se encontraron datos guardados")
        return False
        
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        # Intentar cargar datos mínimos como fallback
        try:
            st.session_state.batch_data = pd.DataFrame({'Azimuth': [], 'Distance': []})
            st.session_state.single_points = pd.DataFrame({'X': [], 'Y': []})
        except:
            pass
        return False

def clear_saved_data():
    """Limpiar datos guardados"""
    try:
        st.components.v1.html("""
        <script>
            window.parent.clearAzimuthData();
        </script>
        """, height=0)
        
        # Limpiar también el almacenamiento de sesión
        if 'saved_data' in st.session_state:
            del st.session_state['saved_data']
            
    except Exception as e:
        st.error(f"Error al limpiar datos: {str(e)}")

def show_toast(message, type="info", duration=3000):
    """Mostrar notificación toast para feedback de usuario"""
    toast_html = f"""
    <div id="toast-notification" style="
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 6px;
        color: white;
        font-weight: 500;
        z-index: 10000;
        opacity: 0;
        transition: opacity 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        max-width: 300px;
        word-wrap: break-word;
    ">
        {message}
    </div>
    <script>
        (function() {{
            const toast = document.getElementById('toast-notification');
            const type = '{type}';
            
            // Set background color based on type
            switch(type) {{
                case 'success':
                    toast.style.backgroundColor = '#28a745';
                    break;
                case 'error':
                    toast.style.backgroundColor = '#dc3545';
                    break;
                case 'warning':
                    toast.style.backgroundColor = '#ffc107';
                    toast.style.color = '#212529';
                    break;
                default:
                    toast.style.backgroundColor = '#17a2b8';
            }}
            
            // Show toast
            setTimeout(function() {{
                toast.style.opacity = '1';
            }}, 100);
            
            // Hide toast after duration
            setTimeout(function() {{
                toast.style.opacity = '0';
                setTimeout(function() {{
                    toast.remove();
                }}, 300);
            }}, {duration});
            
            // Add click to dismiss
            toast.addEventListener('click', function() {{
                toast.style.opacity = '0';
                setTimeout(function() {{
                    toast.remove();
                }}, 300);
            }});
        }})();
    </script>
    """
    
    st.components.v1.html(toast_html, height=0)

def setup_page_config():
    """Configurar la página de Streamlit"""
    st.set_page_config(**APP_CONFIG)
    st.markdown('<div class="offline-indicator">📱 Offline Ready</div>', unsafe_allow_html=True)
    
    # Add mobile viewport meta tag
    st.markdown(
        '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">',
        unsafe_allow_html=True
    )
    
    # Add JavaScript for data loading from localStorage
    st.components.v1.html("""
    <script>
        // Función para cargar datos guardados al iniciar
        function loadSavedDataOnStartup() {
            try {
                const savedData = localStorage.getItem('azimuthAppData');
                if (savedData) {
                    const data = JSON.parse(savedData);
                    
                    // Enviar datos a Streamlit mediante postMessage
                    window.parent.postMessage({
                        type: 'azimuthDataLoaded',
                        data: data
                    }, '*');
                    
                    console.log('Datos de azimut cargados al inicio');
                }
            } catch (e) {
                console.error('Error al cargar datos guardados:', e);
            }
        }
        
        // Cargar datos cuando la página se carga
        window.addEventListener('load', loadSavedDataOnStartup);
        
        // También intentar cargar inmediatamente si el DOM ya está listo
        if (document.readyState === 'complete' || document.readyState === 'interactive') {
            setTimeout(loadSavedDataOnStartup, 100);
        }
    </script>
    """, height=0)

def main():
    """Función principal mejorada con mejor organización y controles de rendimiento"""
    setup_page_config()
    initialize_session_state()
    
    # 💾 AUTO-SAVE: Auto-guardado de datos
    if 'auto_save_enabled' not in st.session_state:
        st.session_state.auto_save_enabled = True
    
    if 'last_save_time' not in st.session_state:
        st.session_state.last_save_time = time.time()
    
    # Auto-save cada 5 segundos si está habilitado
    if st.session_state.auto_save_enabled:
        current_time = time.time()
        if current_time - st.session_state.last_save_time > 5:  # 5 segundos
            save_data_to_local_storage()
            st.session_state.last_save_time = current_time
    
    # 📂 DATA LOADING: Intentar cargar datos guardados al inicio
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
        load_data_from_local_storage()
        
        # Si hay datos cargados, procesarlos
        if 'loaded_azimuth_data' in st.session_state:
            data = st.session_state.loaded_azimuth_data

            # Asegurar que 'data' es un dict válido
            if not isinstance(data, dict):
                if isinstance(data, str):
                    try:
                        data = json.loads(data)
                    except Exception:
                        data = None
                else:
                    data = None

            if isinstance(data, dict):
                # Actualizar DataFrames con datos cargados
                if data.get('batch_data'):
                    st.session_state.batch_data = pd.DataFrame(data['batch_data'])
                
                if data.get('single_points'):
                    st.session_state.single_points = pd.DataFrame(data['single_points'])
                
                if data.get('reference_point'):
                    st.session_state.ref_x = data['reference_point'].get('x', st.session_state.get('ref_x', 1000.0))
                    st.session_state.ref_y = data['reference_point'].get('y', st.session_state.get('ref_y', 1000.0))
                
                st.success("✅ Datos guardados cargados automáticamente")
    
    # 📊 DATA PERSISTENCE STATUS: Mostrar estado del guardado
    if 'data_persistence_status' not in st.session_state:
        st.session_state.data_persistence_status = {
            'last_save': None,
            'has_saved_data': False,
            'auto_save_active': st.session_state.get('auto_save_enabled', True)
        }
    
    # 📡 MESSAGE HANDLER: Recibir datos de JavaScript
    if 'message_handler_setup' not in st.session_state:
        st.session_state.message_handler_setup = True
    
    # 🚀 PERFORMANCE: Sidebar para controles de rendimiento
    with st.sidebar:
        st.header("⚡ Controles de Rendimiento")
        
        # Estadísticas de caché
        if st.button("🧹 Limpiar Caché"):
            st.cache_data.clear()
            st.cache_resource.clear()
            perf_manager._cache_stats.clear()
            st.success("✅ Caché limpiado")
        
        # Optimización de memoria
        if st.button("🗑️ Optimizar Memoria"):
            perf_manager.optimize_memory()
            st.success("✅ Memoria optimizada")
        
        # Mostrar estadísticas
        if st.checkbox("📊 Mostrar estadísticas"):
            stats = perf_manager.get_cache_stats()
            st.metric("Caché hits", stats['cache_hits'])
            st.metric("Uso de memoria (MB)", f"{stats['memory_usage']:.2f}")
        
        # 💾 DATA PERSISTENCE CONTROLS
        st.subheader("💾 Guardar Datos")
        
        # Estado de persistencia
        col_status1, col_status2 = st.columns(2)
        with col_status1:
            if st.session_state.get('auto_save_enabled', True):
                st.success("🟢 Auto-guardado")
            else:
                st.error("🔴 Auto-guardado apagado")
        with col_status2:
            # Verificar si hay datos guardados
            if 'saved_data' in st.session_state:
                st.info("💾 Datos guardados")
            else:
                st.warning("📭 Sin datos guardados")
        
        # Auto-save indicator
        auto_save = st.checkbox("Auto-guardar datos", value=st.session_state.get('auto_save_enabled', True), 
                               help="Guardar automáticamente cada 5 segundos")
        st.session_state.auto_save_enabled = auto_save
        
        # Manual save button
        if st.button("💾 Guardar Ahora", help="Guardar datos actualmente en la aplicación"):
            save_data_to_local_storage()
            show_toast("💾 Datos guardados localmente", "success", 2000)
        
        # Load saved data
        if st.button("📂 Cargar Datos Guardados", help="Cargar datos previamente guardados"):
            load_data_from_local_storage()
            show_toast("📂 Datos cargados desde almacenamiento local", "info", 2000)
        
        # Clear saved data
        if st.button("🗑️ Limpiar Datos Guardados", help="Eliminar datos guardados del navegador"):
            clear_saved_data()
            st.success("🗑️ Datos guardados eliminados")
        
        # 📱 OFFLINE STATUS SECTION
        st.subheader("📱 Estado de Conexión")
        
        # Network status indicator
        col_net1, col_net2 = st.columns([2, 1])
        with col_net1:
            st.components.v1.html("""
                <div id="network-status" style="padding: 5px; border-radius: 5px; font-size: 12px; margin-bottom: 10px;">
                    <span id="status-text">Verificando conexión...</span>
                </div>
                <script>
                    function updateNetworkStatus() {
                        const statusDiv = document.getElementById('network-status');
                        const statusText = document.getElementById('status-text');
                        
                        if (navigator.onLine) {
                            statusDiv.style.backgroundColor = '#d4edda';
                            statusDiv.style.border = '1px solid #c3e6cb';
                            statusDiv.style.color = '#155724';
                            statusText.textContent = '🟢 En línea';
                        } else {
                            statusDiv.style.backgroundColor = '#f8d7da';
                            statusDiv.style.border = '1px solid #f5c6cb';
                            statusDiv.style.color = '#721c24';
                            statusText.textContent = '🔴 Sin conexión';
                        }
                    }
                    
                    window.addEventListener('online', updateNetworkStatus);
                    window.addEventListener('offline', updateNetworkStatus);
                    updateNetworkStatus();
                </script>
            """, height=60)
        
        with col_net2:
            if st.button("🔄 Actualizar", help="Actualizar estado de conexión"):
                st.rerun()
        
        # Storage usage indicator
        st.components.v1.html("""
            <div style="font-size: 11px; color: #666; margin-bottom: 5px;">Uso de almacenamiento:</div>
            <div style="background-color: #e9ecef; border-radius: 3px; height: 8px; overflow: hidden; margin-bottom: 5px;">
                <div id="storage-bar" style="background-color: #28a745; height: 100%; width: 0%; transition: width 0.3s ease;"></div>
            </div>
            <div id="storage-text" style="font-size: 10px; color: #666;">Calculando...</div>
            <script>
                function updateStorageUsage() {
                    if (typeof(Storage) !== "undefined") {
                        try {
                            // Calculate approximate storage usage
                            let totalSize = 0;
                            for (let key in localStorage) {
                                if (localStorage.hasOwnProperty(key)) {
                                    totalSize += localStorage[key].length + key.length;
                                }
                            }
                            
                            // Convert to KB (rough estimate)
                            const sizeKB = Math.round(totalSize / 1024);
                            const maxSizeKB = 5120; // Approximate 5MB limit
                            const percentage = Math.min(100, Math.round((sizeKB / maxSizeKB) * 100));
                            
                            document.getElementById('storage-bar').style.width = percentage + '%';
                            document.getElementById('storage-text').textContent = 
                                sizeKB + ' KB / ~' + maxSizeKB + ' KB (' + percentage + '%)';
                            
                            // Change color based on usage
                            const bar = document.getElementById('storage-bar');
                            if (percentage > 80) {
                                bar.style.backgroundColor = '#dc3545'; // Red
                            } else if (percentage > 60) {
                                bar.style.backgroundColor = '#ffc107'; // Yellow
                            } else {
                                bar.style.backgroundColor = '#28a745'; // Green
                            }
                        } catch (e) {
                            document.getElementById('storage-text').textContent = 'Error al calcular uso';
                        }
                    } else {
                        document.getElementById('storage-text').textContent = 'Almacenamiento no soportado';
                    }
                }
                
                updateStorageUsage();
            </script>
        """, height=80)
        
        # Offline mode controls
        st.write("**Modo sin conexión:**")
        col_off1, col_off2 = st.columns(2)
        with col_off1:
            if st.button("📱 Activar", help="Activar modo sin conexión"):
                st.session_state.offline_mode = True
                show_toast("✅ Modo sin conexión activado", "success", 2000)
                st.rerun()
        
        with col_off2:
            if st.button("🌐 Desactivar", help="Desactivar modo sin conexión"):
                st.session_state.offline_mode = False
                show_toast("✅ Modo sin conexión desactivado", "success", 2000)
                st.rerun()
        
        # Show current offline mode status
        if st.session_state.get('offline_mode', False):
            st.info("📱 Modo sin conexión: ACTIVADO")
            st.write("*Los datos se guardarán localmente*")
        else:
            st.write("*Modo sin conexión: Desactivado*")
        
        # Configuración de rendimiento
        st.subheader("🔧 Configuración")
        use_async = st.checkbox("Procesamiento asíncrono", value=True, 
                               help="Activar para lotes >100 puntos")
        cache_ttl = st.slider("TTL Caché (minutos)", 15, 360, 60,
                             help="Tiempo de vida del caché")
   
    # Initialize session state for points
    if 'single_points' not in st.session_state:
        st.session_state.single_points = pd.DataFrame({
            'X': [],
            'Y': []
        })
   
    if 'batch_data' not in st.session_state:
        st.session_state.batch_data = pd.DataFrame({
            'Azimuth': [],
            'Distance': []
        })
   
    # Sidebar
    st.sidebar.header(get_text('settings', st.session_state.language))
   
    # Language toggle (solo español)
    if st.sidebar.button("🇪🇸 Español", use_container_width=True, type="primary"):
        st.session_state.language = 'es'
        st.rerun()
   
    lang = st.session_state.language
   
    st.title(get_text('title', lang))
    st.markdown(get_text('subtitle', lang))

    # 🚀 PERFORMANCE: Indicador de rendimiento
    col1, col2, col3 = st.columns(3)
    with col1:
        cache_hits = len(perf_manager._cache_stats)
        st.metric("⚡ Caché Hits", cache_hits,
                 help="Número de operaciones aceleradas por caché")
    with col2:
        if PSUTIL_AVAILABLE and psutil is not None:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            st.metric("💻 CPU Uso", f"{cpu_percent}%",
                     help="Uso actual del procesador")
        else:
            st.metric("💻 Estado", "Activo", help="Sistema operativo - optimizado")
    with col3:
        if PSUTIL_AVAILABLE and psutil is not None:
            memory = psutil.virtual_memory()
            st.metric("🧠 Memoria", f"{memory.percent}%",
                     help="Uso de memoria del sistema")
        else:
            memory_estimate = len(perf_manager._cache_stats) * 0.5
            st.metric("🧠 Memoria", f"~{memory_estimate:.1f}MB", 
                     help="Estimación de uso de memoria")
   
    azimuth_convention = "excel"
   
    # Reference point
    st.sidebar.subheader(get_text('reference_point', lang))
    ref_x = st.sidebar.number_input(get_text('reference_x', lang), value=1000.0, help=get_text('reference_x_help', lang))
    ref_y = st.sidebar.number_input(get_text('reference_y', lang), value=1000.0, help=get_text('reference_y_help', lang))
   
    # Opción para fondo del gráfico
    bg_color = st.sidebar.selectbox("Fondo del Gráfico", ['Blanco', 'Negro'])
   
    # Batch Conversion Section
    st.header(get_text('batch_conversion', lang))
   
    # Points management section
    st.subheader("📍 Gestión de Puntos")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
   
    with col_btn1:
        if st.button("➕ Agregar Punto", key="add_point", help="Agregar punto a la visualización",
                    use_container_width=True, type="primary"):
            if 'current_x' in st.session_state and 'current_y' in st.session_state:
                x = st.session_state.current_x
                y = st.session_state.current_y
               
                try:
                    new_point = pd.DataFrame({
                        'X': [x],
                        'Y': [y]
                    })
                   
                    st.session_state.single_points = pd.concat([st.session_state.single_points, new_point], ignore_index=True)
                    st.success(f"✅ ¡Punto agregado! Total puntos: {len(st.session_state.single_points)}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al agregar punto: {str(e)}")
   
    with col_btn2:
        if st.button("🗑️ Limpiar Puntos", key="clear_points", help="Eliminar todos los puntos de la visualización",
                    use_container_width=True):
            st.session_state.single_points = pd.DataFrame({
                'X': [], 'Y': []
            })
            st.success("✅ ¡Todos los puntos eliminados!")
            st.rerun()
   
    with col_btn3:
        st.info(f"**Puntos actuales:** {len(st.session_state.single_points)}")
        if not st.session_state.single_points.empty:
            st.metric("Último Punto", f"({st.session_state.single_points.iloc[-1]['X']:.3f}, {st.session_state.single_points.iloc[-1]['Y']:.3f})")
   
    # Agregar el cálculo del área para puntos ingresados manualmente
    if len(st.session_state.single_points) >= 3:
        coordinates = list(zip(st.session_state.single_points['X'], st.session_state.single_points['Y']))
        single_points_area = calculate_polygon_area(coordinates)
        st.subheader("📐 Área del Polígono de Puntos Ingresados")
        st.metric("Área", f"{single_points_area:.3f} m²")
   
    if not st.session_state.single_points.empty:
        with st.expander("📋 Ver Todos los Puntos", expanded=False):
            st.dataframe(st.session_state.single_points[['X', 'Y']],
                        use_container_width=True, height=200)
   
    st.subheader("📊 Ingreso de Coordenadas")
   
    x_coord = st.number_input(
        get_text('x_input', lang),
        value=0.0,
        step=0.001,
        format="%.3f",
        help=get_text('x_input_help', lang),
        key="x_input"
    )
    st.session_state.current_x = x_coord
   
    y_coord = st.number_input(
        get_text('y_input', lang),
        value=0.0,
        step=0.001,
        format="%.3f",
        help=get_text('y_input_help', lang),
        key="y_input"
    )
    st.session_state.current_y = y_coord
   
    if x_coord != 0 or y_coord != 0:
        st.subheader(get_text('results', lang))
        col_x, col_y = st.columns(2)
        with col_x:
            st.metric(get_text('x_coordinate', lang), f"{x_coord:.3f}")
        with col_y:
            st.metric(get_text('y_coordinate', lang), f"{y_coord:.3f}")
       
        st.write(f"**{get_text('input_summary', lang)}** Coordenadas ({x_coord:.3f}, {y_coord:.3f})")
    else:
        st.info(get_text('enter_values', lang))
   
    st.markdown("---")
    st.subheader("Carga de Datos por Lotes")
   
    # Removed the radio and CSV upload, only manual input
    st.subheader("Ingresar Datos")
   
    if not st.session_state.batch_data.empty:
        st.write("**Datos Actuales:**")
        st.dataframe(st.session_state.batch_data, use_container_width=True, height=250)
   
    if 'form_counter' not in st.session_state:
        st.session_state.form_counter = 0
   
    with st.form(f"add_entry_form_{st.session_state.form_counter}"):
        st.write("**Agregar Nueva Entrada:**")
        col1, col2, col3 = st.columns([2, 1, 1])
   
        with col1:
            new_azimuth = st.text_input(
                "Azimut",
                value="",
                placeholder="26 56 7.00 o 26.935",
                help="Formatos fáciles: 26 56 7.00 | 26-56-7.00 | 26:56:7.00 | 26.935"
            )
   
        with col2:
            new_distance = st.number_input(
                "Distancia",
                value=None,
                step=0.001,
                format="%.3f"
            )
   
        with col3:
            submitted = st.form_submit_button("➕ Agregar Entrada")
           
        if submitted and new_azimuth and new_distance is not None and new_distance > 0:
            new_row = pd.DataFrame({
                'Azimuth': [new_azimuth],
                'Distance': [new_distance]
            })
            st.session_state.batch_data = pd.concat([st.session_state.batch_data, new_row], ignore_index=True)
            st.session_state.form_counter += 1
            st.success("✅ ¡Entrada agregada!")
            st.rerun()
   
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Limpiar Todos los Datos"):
            st.session_state.batch_data = pd.DataFrame({'Azimuth': [], 'Distance': []})
            st.rerun()
    with col2:
        if st.button("📝 Restablecer a Ejemplos"):
            st.session_state.batch_data = pd.DataFrame({
                'Azimuth': ["26 56 7.00", "90-0-0", "180:30:15.5", "270_45_30"],
                'Distance': [5.178, 1.000, 1.000, 1.000]
            })
            st.rerun()
   
    if st.button("🔄 Convertir Todo", type="primary", use_container_width=True):
        if not st.session_state.batch_data.empty:
            results = []
            errors = []
           
            current_ref_x = ref_x
            current_ref_y = ref_y
           
            # 🚀 PERFORMANCE: Indicador de progreso para procesamiento
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Mostrar información de rendimiento
            batch_size = len(st.session_state.batch_data)
            if batch_size > 100:
                status_text.text(f"⚡ Procesando {batch_size} puntos con async...")
            else:
                status_text.text(f"📊 Procesando {batch_size} puntos...")
           
            for index, row in st.session_state.batch_data.iterrows():
                try:
                    azimuth_raw = row['Azimuth']
                    if isinstance(azimuth_raw, str):
                        azimuth = parse_dms_to_decimal(azimuth_raw)
                        if azimuth is None:
                            errors.append(f"Fila {int(index) + 1}: Formato de azimut inválido '{azimuth_raw}'")
                            continue
                    else:
                        azimuth = float(azimuth_raw)
                   
                    distance = float(row['Distance'])
                   
                    if not validate_azimuth(azimuth):
                        errors.append(f"Fila {int(index) + 1}: Azimut inválido {azimuth}°")
                        continue
                   
                    x, y = azimuth_to_coordinates(azimuth, distance, current_ref_x, current_ref_y, azimuth_convention)
                   
                    results.append({
                        'Row': int(index) + 1,
                        'Azimuth_Original': str(azimuth_raw),
                        'Azimuth_Decimal': float(azimuth),
                        'Distance': float(distance),
                        'Reference_X': float(current_ref_x),
                        'Reference_Y': float(current_ref_y),
                        'X_Coordinate': float(x),
                        'Y_Coordinate': float(y)
                    })
                   
                    current_ref_x = x
                    current_ref_y = y
                   
                except Exception as e:
                    errors.append(f"Fila {int(index) + 1}: {str(e)}")
           
            # Actualizar barra de progreso
            progress_bar.progress(100)
            status_text.text(f"✅ Procesamiento completado: {len(results)} puntos calculados")
            
            # 🚀 PERFORMANCE: Actualizar estadísticas
            perf_manager._cache_stats[f'batch_{batch_size}'] = len(results)
           
            if results:
                results_df = pd.DataFrame(results)
                st.session_state['results_df'] = results_df
               
                st.success(f"✅ ¡Convertidos {len(results)} puntos exitosamente!")
           
            if errors:
                st.error("❌ Errores encontrados:")
                for error in errors:
                    st.write(f"- {error}")
        else:
            st.warning("⚠️ No hay datos para convertir")
   
    # Display persistent results
    results_df = st.session_state.get('results_df', pd.DataFrame())
    if not results_df.empty:
        final_x = results_df.iloc[-1]['X_Coordinate']
        final_y = results_df.iloc[-1]['Y_Coordinate']
        closure_error_x = abs(final_x - ref_x)
        closure_error_y = abs(final_y - ref_y)
        closure_error = math.sqrt(closure_error_x**2 + closure_error_y**2)
       
        if closure_error < 0.01:
            st.success(f"🎯 ¡El polígono CIERRA! Error: {closure_error:.6f}")
        else:
            st.error(f"⚠️ Error de cierre: {closure_error:.6f} (X: {closure_error_x:.3f}, Y: {closure_error_y:.3f})")
       
        coordinates = [(ref_x, ref_y)] + list(zip(results_df['X_Coordinate'], results_df['Y_Coordinate']))
        polygon_area = calculate_polygon_area(coordinates)
       
        st.subheader("📐 Área del Polígono Azimut")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Área", f"{polygon_area:.3f} m²")
        with col2:
            st.metric("Vértices", f"{len(results_df)}")
       
        # Comparación de áreas si hay puntos ingresados
        if len(st.session_state.single_points) >= 3:
            single_coords = list(zip(st.session_state.single_points['X'], st.session_state.single_points['Y']))
            single_area = calculate_polygon_area(single_coords)
            area_diff = abs(polygon_area - single_area)
            st.subheader("📏 Comparación de Áreas")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Área Azimut", f"{polygon_area:.3f} m²")
            with col2:
                st.metric("Área Puntos", f"{single_area:.3f} m²")
            with col3:
                st.metric("Diferencia", f"{area_diff:.3f} m²")
       
        displayed_df = results_df.drop(columns=['Reference_X', 'Reference_Y'])
        column_config = {
            'Row': st.column_config.NumberColumn('Pt', width='small'),
            'Azimuth_Original': st.column_config.TextColumn('Azimut Original', width='medium'),
            'Azimuth_Decimal': st.column_config.NumberColumn('Azimut Decimal', width='medium'),
            'Distance': st.column_config.NumberColumn('Distancia', width='small'),
            'X_Coordinate': st.column_config.NumberColumn('X', width='medium'),
            'Y_Coordinate': st.column_config.NumberColumn('Y', width='medium')
        }
        st.dataframe(displayed_df, column_config=column_config, use_container_width=True, height=300)
       
        csv_buffer = io.StringIO()
        displayed_df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
       
        st.download_button(
            label="📥 Descargar Resultados como CSV",
            data=csv_data,
            file_name="azimuth_results.csv",
            mime="text/csv",
            use_container_width=True
        )

        txt_buffer = io.StringIO()
        txt_buffer.write("pt,x,y\n")
        for _, row in results_df.iterrows():
            txt_buffer.write(f"{int(row['Row'])},{row['X_Coordinate']:.3f},{row['Y_Coordinate']:.3f}\n")
        txt_data = txt_buffer.getvalue()
       
        st.download_button(
            label="📥 Descargar Coordenadas como TXT (pt,x,y)",
            data=txt_data,
            file_name="coordenadas.txt",
            mime="text/plain",
            use_container_width=True
        )
   
    # Visualization Section (moved below "Convertir Todo")
    st.subheader(get_text('visualization', lang))
   
    results_df = st.session_state.get('results_df', pd.DataFrame())
    try:
        fig, config = create_multi_point_plot(st.session_state.single_points, results_df, ref_x, ref_y, x_coord, y_coord, lang, bg_color)
        
        # Enhanced responsive configuration for mobile
        responsive_config = config.copy()
        responsive_config.update({
            'responsive': True,
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'resetScale2d'],
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'azimuth_plot_mobile',
                'height': 600,
                'width': 800,
                'scale': 1
            }
        })
        
        st.plotly_chart(fig, use_container_width=True, config=responsive_config)
    except Exception as e:
        st.error(f"Error de visualización: {str(e)}")
   
    with st.expander("ℹ️ Cómo usar la visualización"):
        st.markdown("""
        **Controles Interactivos:**
        - 🏠 **Inicio**: Restablecer vista
        - 🔍 **Zoom**: Acercar/alejar
        - ↔️ **Desplazar**: Arrastrar para mover
        - 📷 **Cámara**: Descargar como PNG
        - 🖱️ **Rueda**: Zoom con la rueda del ratón
        - 🖐️ **Doble clic**: Restablecer zoom
       
        **Leyenda:**
        - 🔵 **Círculo Azul (REF)**: Punto de referencia
        - 🔴 **Diamantes (P1, P2, ...)**: Puntos ingresados directamente
        - 🔴 **Círculos (A1, A2, ...)**: Puntos del polígono (de azimuts)
        - 🟢 **X Verde**: Punto actual (vista previa)
        - 🔵 **Línea Azul**: Perímetro del polígono (azimut)
        - 🟢 **Línea Verde**: Perímetro del polígono (puntos ingresados)
        - ➡️ **Flechas**: Dirección del polígono (azimut)
        """)
if __name__ == "__main__":
    main()
