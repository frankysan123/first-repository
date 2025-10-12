import streamlit as st
import numpy as np
import pandas as pd
import math
import io
import re
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# To show a hit counter image in Streamlit, use markdown with unsafe_allow_html=True
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
</style>
""", unsafe_allow_html=True)

# Language translations (keeping original translations)
TRANSLATIONS = {
    'en': {
        'title': '🧭 Azimuth to Coordinates Converter',
        'subtitle': 'Convert azimuth and distance measurements to X,Y coordinates using your exact Excel formulas.',
        'settings': '⚙️ Settings',
        'language': '🌍 Language',
        'reference_point': 'Reference Point',
        'reference_x': 'Reference X',
        'reference_y': 'Reference Y',
        'reference_x_help': 'X coordinate of reference point',
        'reference_y_help': 'Y coordinate of reference point',
        'single_conversion': '📍 Single Conversion',
        'batch_conversion': '📊 Batch Conversion',
        'instructions': 'ℹ️ Instructions',
        'single_point_conversion': 'Single Point Conversion',
        'azimuth_input_format': 'Azimuth Input Format',
        'dms_format': 'DMS (266°56\'7.24")',
        'decimal_format': 'Decimal (266.935)',
        'azimuth_easy_input': 'Azimuth (Easy Mobile Input)',
        'azimuth_placeholder': 'Easy formats: 26 56 7.00 or 26-56-7.00 or 26:56:7.00',
        'azimuth_help': 'Mobile-friendly formats:\n• Spaces: 26 56 7.00\n• Dashes: 26-56-7.00\n• Colons: 26:56:7.00\n• Traditional: 26°56\'7.00"',
        'azimuth_decimal': 'Azimuth (decimal degrees)',
        'azimuth_decimal_help': 'Enter azimuth angle in decimal degrees (0-360)',
        'distance': 'Distance',
        'distance_help': 'Enter distance from reference point',
        'results': '📍 Results',
        'x_coordinate': 'X Coordinate',
        'y_coordinate': 'Y Coordinate',
        'input_summary': 'Input:',
        'enter_values': '👈 Enter azimuth and distance values to see results',
        'calculation_error': '❌ Calculation Error:',
        'parsed_success': '✅ Parsed:',
        'parse_error': '❌ Could not parse',
        'try_format': 'Try format like: 45°30\'15" or 120°0\'0\'\'',
        'azimuth_warning': '⚠️ Azimuth {:.3f}° is outside 0-360° range',
        'enter_azimuth': '👆 Enter an azimuth value above',
        'visualization': '📈 Visualization',
    },
    'es': {
        'title': '🧭 Convertidor de Azimut a Coordenadas',
        'subtitle': 'Convierte medidas de azimut y distancia a coordenadas X,Y usando tus fórmulas exactas de Excel.',
        'settings': '⚙️ Configuración',
        'language': '🌍 Idioma',
        'reference_point': 'Punto de Referencia',
        'reference_x': 'Referencia X',
        'reference_y': 'Referencia Y',
        'reference_x_help': 'Coordenada X del punto de referencia',
        'reference_y_help': 'Coordenada Y del punto de referencia',
        'single_conversion': '📍 Conversión Individual',
        'batch_conversion': '📊 Conversión por Lotes',
        'instructions': 'ℹ️ Instrucciones',
        'single_point_conversion': 'Conversión de Punto Individual',
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
        'input_summary': 'Entrada:',
        'enter_values': '👈 Ingresa valores de azimut y distancia para ver resultados',
        'calculation_error': '❌ Error de Cálculo:',
        'parsed_success': '✅ Analizado:',
        'parse_error': '❌ No se pudo analizar',
        'try_format': 'Intenta formato como: 45°30\'15" o 120°0\'0\'\'',
        'azimuth_warning': '⚠️ Azimut {:.3f}° está fuera del rango 0-360°',
        'enter_azimuth': '👆 Ingresa un valor de azimut arriba',
        'visualization': '📈 Visualización',
    }
}

def get_text(key, lang='en'):
    """Get translated text for the given key and language"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

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

def create_single_point_plot(ref_x, ref_y, x, y, azimuth, distance, lang='en'):
    """Create interactive plot for single point conversion"""
    fig = go.Figure()
    
    # Reference point
    fig.add_trace(go.Scatter(
        x=[ref_x],
        y=[ref_y],
        mode='markers+text',
        name='Reference',
        marker=dict(color='blue', size=16, symbol='circle'),
        text=['REF'],
        textposition='bottom center',
        textfont=dict(size=14, color='blue'),
        hovertemplate='<b>Reference</b><br>X: %{x:.3f}<br>Y: %{y:.3f}<extra></extra>'
    ))
    
    # Calculated point
    fig.add_trace(go.Scatter(
        x=[x],
        y=[y],
        mode='markers+text',
        name='Target Point',
        marker=dict(color='red', size=16, symbol='diamond'),
        text=['P1'],
        textposition='top center',
        textfont=dict(size=14, color='red'),
        hovertemplate='<b>Point</b><br>X: %{x:.3f}<br>Y: %{y:.3f}<extra></extra>'
    ))
    
    # Line connecting points
    fig.add_trace(go.Scatter(
        x=[ref_x, x],
        y=[ref_y, y],
        mode='lines',
        name=f'Azimuth {azimuth:.2f}°',
        line=dict(color='green', width=3, dash='dash'),
        hovertemplate=f'<b>Distance: {distance:.3f}</b><extra></extra>'
    ))
    
    # Add arrow annotation
    fig.add_annotation(
        x=x,
        y=y,
        ax=ref_x,
        ay=ref_y,
        xref='x',
        yref='y',
        axref='x',
        ayref='y',
        showarrow=True,
        arrowhead=2,
        arrowsize=1.5,
        arrowwidth=2,
        arrowcolor='green'
    )
    
    fig.update_layout(
        title={
            'text': f'Azimuth Conversion: {azimuth:.2f}° | Distance: {distance:.3f}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        xaxis_title='X (m)',
        yaxis_title='Y (m)',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        hovermode='closest',
        height=600,
        yaxis=dict(scaleanchor="x", scaleratio=1),
        plot_bgcolor='rgba(240,240,240,0.5)',
        dragmode='pan'
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200,200,200,0.5)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(200,200,200,0.5)')
    
    config = {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarStyle': {
            'bgcolor': 'rgba(30, 30, 30, 0.95)',
            'color': 'white'
        },
        'modeBarButtonSize': 20,
        'doubleClick': 'reset',
        'scrollZoom': True
    }
    
    return fig, config

def create_polygon_plot(results_df, ref_x, ref_y, lang='en'):
    """Create interactive plot for polygon traversal"""
    fig = go.Figure()
    
    # Extract all coordinates including initial reference
    all_x = [ref_x] + results_df['X_Coordinate'].tolist()
    all_y = [ref_y] + results_df['Y_Coordinate'].tolist()
    
    # Polygon outline
    fig.add_trace(go.Scatter(
        x=all_x + [all_x[0]],  # Close the polygon
        y=all_y + [all_y[0]],
        mode='lines',
        name='Polygon',
        line=dict(color='blue', width=3),
        fill='toself',
        fillcolor='rgba(31, 119, 180, 0.2)',
        hoverinfo='skip'
    ))
    
    # Reference point
    fig.add_trace(go.Scatter(
        x=[ref_x],
        y=[ref_y],
        mode='markers+text',
        name='Start/End',
        marker=dict(color='green', size=18, symbol='star'),
        text=['START'],
        textposition='bottom center',
        textfont=dict(size=12, color='green', family='Arial Black'),
        hovertemplate='<b>Start Point</b><br>X: %{x:.3f}<br>Y: %{y:.3f}<extra></extra>'
    ))
    
    # All calculated points
    if len(results_df) <= 20:  # Show labels only if <= 20 points
        labels = [f'P{i+1}' for i in range(len(results_df))]
        mode = 'markers+text'
    else:
        labels = None
        mode = 'markers'
    
    fig.add_trace(go.Scatter(
        x=results_df['X_Coordinate'],
        y=results_df['Y_Coordinate'],
        mode=mode,
        name='Points',
        marker=dict(color='red', size=10, symbol='circle'),
        text=labels,
        textposition='top center',
        textfont=dict(size=9),
        hovertemplate='<b>Point %{pointNumber}</b><br>X: %{x:.3f}<br>Y: %{y:.3f}<extra></extra>'
    ))
    
    # Add azimuth lines with arrows
    for i, row in results_df.iterrows():
        if i == 0:
            start_x, start_y = ref_x, ref_y
        else:
            start_x = results_df.iloc[i-1]['X_Coordinate']
            start_y = results_df.iloc[i-1]['Y_Coordinate']
        
        # Add arrow annotation for each segment
        fig.add_annotation(
            x=row['X_Coordinate'],
            y=row['Y_Coordinate'],
            ax=start_x,
            ay=start_y,
            xref='x',
            yref='y',
            axref='x',
            ayref='y',
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1.5,
            arrowcolor='rgba(0,100,200,0.5)',
            text=f"Az: {row['Azimuth_Decimal']:.1f}°",
            font=dict(size=8, color='darkblue'),
            bgcolor='rgba(255,255,255,0.7)',
            standoff=5
        )
    
    # Calculate polygon area
    coordinates = [(ref_x, ref_y)] + list(zip(results_df['X_Coordinate'], results_df['Y_Coordinate']))
    area = calculate_polygon_area(coordinates)
    
    fig.update_layout(
        title={
            'text': f'Polygon Traversal | Points: {len(results_df)} | Area: {area:.3f} m²',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        xaxis_title='X (m)',
        yaxis_title='Y (m)',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
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
        'modeBarStyle': {
            'bgcolor': 'rgba(30, 30, 30, 0.95)',
            'color': 'white'
        },
        'modeBarButtonSize': 20,
        'doubleClick': 'reset',
        'scrollZoom': True,
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'polygon_plot',
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
    
    # Offline indicator
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
        st.session_state.language = 'en'
    
    # Sidebar
    st.sidebar.header(get_text('settings', st.session_state.language))
    
    # Language toggle
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🇺🇸 English", use_container_width=True, type="primary" if st.session_state.language == 'en' else "secondary"):
            st.session_state.language = 'en'
            st.rerun()
    with col2:
        if st.button("🇪🇸 Español", use_container_width=True, type="primary" if st.session_state.language == 'es' else "secondary"):
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
    
    # Tabs
    tab1, tab2 = st.tabs([get_text('single_conversion', lang), get_text('batch_conversion', lang)])
    
    with tab1:
        st.header(get_text('single_point_conversion', lang))
        
        col1, col2 = st.columns([1, 1.4])
        
        with col1:
            # Input method
            input_method = st.radio(
                get_text('azimuth_input_format', lang),
                [get_text('dms_format', lang), get_text('decimal_format', lang)],
                horizontal=True
            )
            
            if input_method.startswith(get_text('dms_format', lang)[:3]):
                azimuth_input = st.text_input(
                    get_text('azimuth_easy_input', lang),
                    value="",
                    placeholder=get_text('azimuth_placeholder', lang),
                    help=get_text('azimuth_help', lang)
                )
                
                if azimuth_input:
                    azimuth = parse_dms_to_decimal(azimuth_input)
                    if azimuth is None:
                        st.error(f"{get_text('parse_error', lang)} '{azimuth_input}'. {get_text('try_format', lang)}")
                        azimuth = 0.0
                    else:
                        st.success(f"{get_text('parsed_success', lang)} {azimuth_input} → {azimuth:.8f}°")
                        if not validate_azimuth(azimuth):
                            st.warning(get_text('azimuth_warning', lang).format(azimuth))
                else:
                    azimuth = 0.0
                    st.info(get_text('enter_azimuth', lang))
            else:
                azimuth = st.number_input(
                    get_text('azimuth_decimal', lang),
                    min_value=0.0,
                    max_value=360.0,
                    value=0.0,
                    step=0.001,
                    format="%.3f",
                    help=get_text('azimuth_decimal_help', lang)
                )
            
            distance = st.number_input(
                get_text('distance', lang),
                min_value=0.0,
                value=1.0,
                step=0.001,
                format="%.3f",
                help=get_text('distance_help', lang)
            )
            
            # Results
            if azimuth > 0 or distance > 0:
                try:
                    x, y = azimuth_to_coordinates(azimuth, distance, ref_x, ref_y, azimuth_convention)
                    
                    st.subheader(get_text('results', lang))
                    col_x, col_y = st.columns(2)
                    with col_x:
                        st.metric(get_text('x_coordinate', lang), f"{x:.3f}")
                    with col_y:
                        st.metric(get_text('y_coordinate', lang), f"{y:.3f}")
                    
                    st.write(f"**{get_text('input_summary', lang)}** Azimuth {azimuth:.3f}°, {get_text('distance', lang)} {distance}, {get_text('reference_point', lang)} ({ref_x}, {ref_y})")
                        
                except Exception as e:
                    st.error(f"{get_text('calculation_error', lang)} {str(e)}")
            else:
                st.info(get_text('enter_values', lang))
        
        with col2:
            st.subheader(get_text('visualization', lang))
            
            if azimuth > 0 or distance > 0:
                try:
                    x, y = azimuth_to_coordinates(azimuth, distance, ref_x, ref_y, azimuth_convention)
                    fig, config = create_single_point_plot(ref_x, ref_y, x, y, azimuth, distance, lang)
                    st.plotly_chart(fig, use_container_width=True, config=config)
                except Exception as e:
                    st.error(f"Visualization error: {str(e)}")
            else:
                st.info("👈 Enter values to see visualization")
    
    with tab2:
        st.header("Batch Conversion & Polygon Visualization")
        
        # Initialize session state
        if 'batch_data' not in st.session_state:
            st.session_state.batch_data = pd.DataFrame({
                'Azimuth': [],
                'Distance': []
            })
        
        # Input method
        input_method = st.radio(
            "Input Method",
            ["Manual Entry", "Upload CSV"],
            horizontal=True
        )
        
        col_input, col_viz = st.columns([1, 1.4])
        
        with col_input:
            if input_method == "Manual Entry":
                st.subheader("Enter Data")
                
                # Initialize input fields in session state
                if 'quick_az_input' not in st.session_state:
                    st.session_state.quick_az_input = ""
                if 'quick_dist_input' not in st.session_state:
                    st.session_state.quick_dist_input = 0.0
                
                # Editable data table
                if not st.session_state.batch_data.empty:
                    st.write("**Current Data (Editable):**")
                    
                    # Use data_editor for inline editing
                    edited_df = st.data_editor(
                        st.session_state.batch_data,
                        use_container_width=True,
                        num_rows="dynamic",  # Allow adding/deleting rows
                        height=250,
                        column_config={
                            "Azimuth": st.column_config.TextColumn(
                                "Azimuth",
                                help="Format: 26 56 7.00 or 26.935",
                                width="medium",
                                required=True
                            ),
                            "Distance": st.column_config.NumberColumn(
                                "Distance",
                                help="Distance from reference point",
                                format="%.3f",
                                min_value=0.0,
                                step=0.001,
                                required=True
                            ),
                        },
                        key="data_editor"
                    )
                    
                    # Update session state only if data changed
                    if not edited_df.equals(st.session_state.batch_data):
                        st.session_state.batch_data = edited_df
                
                # Quick add form
                st.write("**Quick Add Entry:**")
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    new_azimuth = st.text_input(
                        "Azimuth", 
                        value=st.session_state.quick_az_input,
                        placeholder="26 56 7.00 or 26.935",
                        help="Easy mobile formats: 26 56 7.00 | 26-56-7.00 | 26:56:7.00 | 26.935",
                        key="quick_azimuth_input"
                    )
                    # Update session state with current value
                    st.session_state.quick_az_input = new_azimuth
                
                with col2:
                    new_distance = st.number_input(
                        "Distance", 
                        value=st.session_state.quick_dist_input,
                        step=0.001, 
                        format="%.3f",
                        min_value=0.0,
                        key="quick_distance_input"
                    )
                    # Update session state with current value
                    st.session_state.quick_dist_input = new_distance
                
                with col3:
                    st.write("")  # Spacing
                    st.write("")  # Spacing
                    if st.button("➕ Add", use_container_width=True, type="primary"):
                        if new_azimuth.strip() and new_distance > 0:
                            new_row = pd.DataFrame({
                                'Azimuth': [new_azimuth.strip()], 
                                'Distance': [new_distance]
                            })
                            st.session_state.batch_data = pd.concat([st.session_state.batch_data, new_row], ignore_index=True)
                            
                            # DON'T clear inputs - keep them for repeated entries
                            st.success("✅ Added! (Inputs kept for next entry)")
                        else:
                            st.warning("⚠️ Enter valid values")
                
                # Optional: Clear inputs button
                if st.button("🔄 Clear Input Fields", use_container_width=True):
                    st.session_state.quick_az_input = ""
                    st.session_state.quick_dist_input = 0.0
                    st.rerun()
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Clear All Data", use_container_width=True):
                        st.session_state.batch_data = pd.DataFrame({'Azimuth': [], 'Distance': []})
                        st.rerun()
                with col2:
                    if st.button("📝 Load Examples", use_container_width=True):
                        st.session_state.batch_data = pd.DataFrame({
                            'Azimuth': ["26 56 7.00", "90-0-0", "180:30:15.5", "270_45_30"],
                            'Distance': [5.178, 1.000, 1.000, 1.000]
                        })
                        st.rerun()
                
            else:  # Upload CSV
                uploaded_file = st.file_uploader(
                    "Upload CSV file",
                    type=['csv'],
                    help="CSV should have columns: Azimuth (DMS or decimal), Distance"
                )
                
                if uploaded_file is not None:
                    try:
                        uploaded_df = pd.read_csv(uploaded_file)
                        if 'Azimuth' in uploaded_df.columns and 'Distance' in uploaded_df.columns:
                            st.session_state.batch_data = uploaded_df[['Azimuth', 'Distance']]
                            st.success("✅ File uploaded successfully!")
                            st.dataframe(st.session_state.batch_data)
                        else:
                            st.error("❌ CSV must contain 'Azimuth' and 'Distance' columns")
                    except Exception as e:
                        st.error(f"❌ Error reading file: {str(e)}")
            
            # Process button
            if st.button("🔄 Convert All", type="primary", use_container_width=True):
                if not st.session_state.batch_data.empty:
                    results = []
                    errors = []
                    
                    current_ref_x = ref_x
                    current_ref_y = ref_y
                    
                    st.info("🔄 Processing polygon traversal...")
                    
                    for index, row in st.session_state.batch_data.iterrows():
                        try:
                            azimuth_raw = row['Azimuth']
                            if isinstance(azimuth_raw, str):
                                azimuth = parse_dms_to_decimal(azimuth_raw)
                                if azimuth is None:
                                    errors.append(f"Row {int(index) + 1}: Invalid azimuth format '{azimuth_raw}'")
                                    continue
                            else:
                                azimuth = float(azimuth_raw)
                            
                            distance = float(row['Distance'])
                            
                            if not validate_azimuth(azimuth):
                                errors.append(f"Row {int(index) + 1}: Invalid azimuth {azimuth}°")
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
                            errors.append(f"Row {int(index) + 1}: {str(e)}")
                    
                    if results:
                        results_df = pd.DataFrame(results)
                        st.session_state['results_df'] = results_df
                        
                        st.success(f"✅ Successfully converted {len(results)} points")
                        
                        # Closure check
                        final_x = results_df.iloc[-1]['X_Coordinate']
                        final_y = results_df.iloc[-1]['Y_Coordinate']
                        closure_error_x = abs(final_x - ref_x)
                        closure_error_y = abs(final_y - ref_y)
                        closure_error = math.sqrt(closure_error_x**2 + closure_error_y**2)
                        
                        if closure_error < 0.01:
                            st.success(f"🎯 Polygon CLOSES! Error: {closure_error:.6f}")
                        else:
                            st.error(f"⚠️ Closure error: {closure_error:.6f} (X: {closure_error_x:.3f}, Y: {closure_error_y:.3f})")
                        
                        # Calculate area
                        coordinates = [(ref_x, ref_y)]
                        for _, row in results_df.iterrows():
                            coordinates.append((row['X_Coordinate'], row['Y_Coordinate']))
                        
                        polygon_area = calculate_polygon_area(coordinates)
                        
                        st.subheader("📐 Polygon Area")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Area", f"{polygon_area:.3f} m²")
                        with col2:
                            st.metric("Vertices", f"{len(results)}")
                        
                        st.dataframe(results_df, use_container_width=True, height=300)
                        
                        # Download button
                        csv_buffer = io.StringIO()
                        results_df.to_csv(csv_buffer, index=False)
                        csv_data = csv_buffer.getvalue()
                        
                        st.download_button(
                            label="📥 Download Results as CSV",
                            data=csv_data,
                            file_name="azimuth_results.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    
                    if errors:
                        st.error("❌ Errors encountered:")
                        for error in errors:
                            st.write(f"- {error}")
                else:
                    st.warning("⚠️ No data to convert")
        
        with col_viz:
            st.subheader("📈 Polygon Visualization")
            
            if 'results_df' in st.session_state and not st.session_state['results_df'].empty:
                try:
                    fig, config = create_polygon_plot(st.session_state['results_df'], ref_x, ref_y, lang)
                    st.plotly_chart(fig, use_container_width=True, config=config)
                    
                    with st.expander("ℹ️ How to use the visualization"):
                        st.markdown("""
                        **Interactive Controls:**
                        - 🏠 **Home**: Reset view
                        - 🔍 **Zoom**: Zoom in/out
                        - ↔️ **Pan**: Drag to move
                        - 📷 **Camera**: Download as PNG
                        - 🖱️ **Scroll**: Zoom with mouse wheel
                        - 🖐️ **Double click**: Reset zoom
                        
                        **Legend:**
                        - 🟢 **Green Star**: Start/End reference point
                        - 🔴 **Red Circles**: Calculated vertices
                        - 🔵 **Blue Line**: Polygon perimeter
                        - ➡️ **Arrows**: Azimuth direction with angles
                        """)
                except Exception as e:
                    st.error(f"Visualization error: {str(e)}")
            else:
                st.info("👈 Enter data and click 'Convert All' to see polygon visualization")
                
                # Show example visualization
                st.markdown("**Example: Square Polygon**")
                example_df = pd.DataFrame({
                    'Row': [1, 2, 3, 4],
                    'Azimuth_Decimal': [0, 90, 180, 270],
                    'Distance': [10, 10, 10, 10],
                    'Reference_X': [1000, 1000, 1010, 1010],
                    'Reference_Y': [1000, 1010, 1010, 1000],
                    'X_Coordinate': [1000, 1010, 1010, 1000],
                    'Y_Coordinate': [1010, 1010, 1000, 1000]
                })
                try:
                    fig_example, config = create_polygon_plot(example_df, 1000, 1000, lang)
                    st.plotly_chart(fig_example, use_container_width=True, config=config)
                except:
                    pass

if __name__ == "__main__":
    main()
