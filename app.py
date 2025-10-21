import streamlit as st
import numpy as np
import pandas as pd
import math
import io
import re
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# To show a hit counter image in Streamlit
st.markdown(
    '<img src="https://hitscounter.dev/api/hit?url=https%3A%2F%2Fpolar2xy.streamlit.app%2F&label=visitas&icon=github&color=%233dd5f3&message=&style=flat&tz=UTC">',
    unsafe_allow_html=True
)

# Custom CSS for better UI
st.markdown("""
<style>
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.5rem !important;
        }
    }
    
    .main-header {
        font-size: 2.2rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
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
</style>
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

def get_text(key, lang='es'):
    """Get translated text for the given key and language"""
    return TRANSLATIONS['es'].get(key, key)

def calculate_polygon_area(coordinates):
    """Calculate polygon area using the Shoelace formula"""
    if len(coordinates) < 3:
        return 0.0
    
    n = len(coordinates)
    area = 0.0
    
    for i in range(n):
        j = (i + 1) % n
        area += coordinates[i][0] * coordinates[j][1]
        area -= coordinates[i][1] * coordinates[j][0]
    
    return abs(area) / 2.0

def azimuth_to_coordinates(azimuth, distance, ref_x=0.0, ref_y=0.0, azimuth_convention="north"):
    """Convert azimuth and distance to X,Y coordinates using Excel formulas"""
    azimuth_rad = math.radians(azimuth)
    x_offset = math.sin(azimuth_rad) * distance
    y_offset = distance * math.cos(azimuth_rad)
    x = ref_x + x_offset
    y = ref_y + y_offset
    return round(x, 3), round(y, 3)

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

def create_multi_point_plot(single_points, results_df, ref_x, ref_y, x_coord, y_coord, lang='es'):
    """Create interactive plot for multiple points and polygon"""
    fig = go.Figure()
    
    # Reference point
    fig.add_trace(go.Scatter(
        x=[ref_x],
        y=[ref_y],
        mode='markers+text',
        name='Referencia',
        marker=dict(color='blue', size=16, symbol='circle'),
        text=['REF'],
        textposition='bottom center',
        textfont=dict(size=14, color='blue'),
        hovertemplate='<b>Referencia</b><br>X: %{x:.3f}<br>Y: %{y:.3f}<extra></extra>'
    ))
    
    # Directly entered points (from single_points)
    single_points_area = 0.0  # Initialize area for single points polygon
    if not single_points.empty:
        colors = ['red', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        
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
            
            fig.add_trace(go.Scatter(
                x=all_x,
                y=all_y,
                mode='lines',
                name='Polígono (Puntos Ingresados)',
                line=dict(color='green', width=3),
                fill='toself',
                fillcolor='rgba(40, 167, 69, 0.2)',  # Light green fill
                hoverinfo='skip'
            ))
            
            # Calculate area for single points polygon
            coordinates = list(zip(single_points['X'], single_points['Y']))
            single_points_area = calculate_polygon_area(coordinates)
    
    # Current preview point (if entered)
    if x_coord != 0 or y_coord != 0:
        fig.add_trace(go.Scatter(
            x=[x_coord],
            y=[y_coord],
            mode='markers',
            name='Punto Actual (Vista Previa)',
            marker=dict(color='green', size=14, symbol='x'),
            hovertemplate='<b>Punto Actual</b><br>X: %{x:.3f}<br>Y: %{y:.3f}<extra></extra>'
        ))
    
    # Polygon points (from results_df)
    polygon_area = 0.0  # Initialize area for azimuth-based polygon
    if not results_df.empty:
        all_x = [ref_x] + results_df['X_Coordinate'].tolist()
        all_y = [ref_y] + results_df['Y_Coordinate'].tolist()
        
        # Polygon trace
        fig.add_trace(go.Scatter(
            x=all_x + [all_x[0]],
            y=all_y + [all_y[0]],
            mode='lines',
            name='Polígono (Azimut)',
            line=dict(color='blue', width=3),
            fill='toself',
            fillcolor='rgba(31, 119, 180, 0.2)',
            hoverinfo='skip'
        ))
        
        # Polygon points
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
            marker=dict(color='red', size=10, symbol='circle'),
            text=labels,
            textposition='top center',
            textfont=dict(size=9),
            hovertemplate='<b>Punto A%{pointNumber}</b><br>X: %{x:.3f}<br>Y: %{y:.3f}<extra></extra>'
        ))
        
        # Arrows for polygon direction
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
                arrowsize=1,
                arrowwidth=1.5,
                arrowcolor='rgba(0,100,200,0.5)',
                text="",
                font=dict(size=15, color='darkblue'),
                bgcolor='rgba(0,0,0,0)',
                borderpad=0,
                standoff=5
            )
        
        # Calculate polygon area
        coordinates = [(ref_x, ref_y)] + list(zip(results_df['X_Coordinate'], results_df['Y_Coordinate']))
        polygon_area = calculate_polygon_area(coordinates)
    
    # Update layout
    title_text = (f'| Puntos Ingresados: {len(single_points)} '
                  f'| Área Puntos: {single_points_area:.3f} m² '
                  f'| Puntos Polígono Azimut: {len(results_df)} '
                  f'| Área Azimut: {polygon_area:.3f} m²')
    fig.update_layout(
        title={
            'text': title_text,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        xaxis_title='X (m)',
        yaxis_title='Y (m)',
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        ),
        hovermode='closest',
        height=700,
        yaxis=dict(scaleanchor="x", scaleratio=1),
        plot_bgcolor='rgba(240,240,240,0.5)',
        dragmode='pan'
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200,200,200,0.5)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200,200,200,0.5)')
    
    config = {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonSize': 20,
        'doubleClick': 'reset',
        'scrollZoom': True,
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'combined_plot',
            'height': 1000,
            'width': 1400,
            'scale': 2
        }
    }
    
    return fig, config

def main():
    st.set_page_config(
        page_title="Azimuth Converter",
        page_icon="🧭",
        layout="wide",
        initial_sidebar_state="auto"
    )
    
    st.markdown("""
    <style>
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
    </style>
    <div class="offline-indicator">📱 Offline Ready</div>
    """, unsafe_allow_html=True)
    
    # Initialize language
    if 'language' not in st.session_state:
        st.session_state.language = 'es'
    
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
    
    azimuth_convention = "excel"
    
    # Reference point
    st.sidebar.subheader(get_text('reference_point', lang))
    ref_x = st.sidebar.number_input(get_text('reference_x', lang), value=1000.0, help=get_text('reference_x_help', lang))
    ref_y = st.sidebar.number_input(get_text('reference_y', lang), value=1000.0, help=get_text('reference_y_help', lang))
    
    # Batch Conversion Tab
    st.header(get_text('batch_conversion', lang))
    
    col_input, col_viz = st.columns([1, 1.4])
    
    with col_input:
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
        
        input_method_batch = st.radio(
            "Método de Ingreso",
            ["Entrada Manual", "Cargar CSV"],
            horizontal=True
        )
        
        if input_method_batch == "Entrada Manual":
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
            
        else:
            uploaded_file = st.file_uploader(
                "Cargar archivo CSV",
                type=['csv'],
                help="El CSV debe tener columnas: Azimuth (GMS o decimal), Distance"
            )
            
            if uploaded_file is not None:
                try:
                    uploaded_df = pd.read_csv(uploaded_file)
                    if 'Azimuth' in uploaded_df.columns and 'Distance' in uploaded_df.columns:
                        st.session_state.batch_data = uploaded_df[['Azimuth', 'Distance']]
                        st.success("✅ ¡Archivo cargado exitosamente!")
                        st.dataframe(st.session_state.batch_data)
                    else:
                        st.error("❌ El CSV debe contener las columnas 'Azimuth' y 'Distance'")
                except Exception as e:
                    st.error(f"❌ Error al leer el archivo: {str(e)}")
        
        if st.button("🔄 Convertir Todo", type="primary", use_container_width=True):
            if not st.session_state.batch_data.empty:
                results = []
                errors = []
                
                current_ref_x = ref_x
                current_ref_y = ref_y
                
                st.info("🔄 Procesando recorrido poligonal...")
                
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
                
                if results:
                    results_df = pd.DataFrame(results)
                    st.session_state['results_df'] = results_df
                    
                    st.success(f"✅ ¡Convertidos {len(results)} puntos exitosamente!")
                    
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
                        st.metric("Vértices", f"{len(results)}")
                    
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
                    
                    st.dataframe(results_df, use_container_width=True, height=300)
                    
                    csv_buffer = io.StringIO()
                    results_df.to_csv(csv_buffer, index=False)
                    csv_data = csv_buffer.getvalue()
                    
                    st.download_button(
                        label="📥 Descargar Resultados como CSV",
                        data=csv_data,
                        file_name="azimuth_results.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                if errors:
                    st.error("❌ Errores encontrados:")
                    for error in errors:
                        st.write(f"- {error}")
            else:
                st.warning("⚠️ No hay datos para convertir")
    
    with col_viz:
        st.subheader(get_text('visualization', lang))
        
        results_df = st.session_state.get('results_df', pd.DataFrame())
        try:
            fig, config = create_multi_point_plot(st.session_state.single_points, results_df, ref_x, ref_y, x_coord, y_coord, lang)
            st.plotly_chart(fig, use_container_width=True, config=config)
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
            - 🔵 **Línea Azul**: Perímetro del polígono
            - ➡️ **Flechas**: Dirección del azimut
            """)

if __name__ == "__main__":
    main()
