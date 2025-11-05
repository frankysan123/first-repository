import streamlit as st
import numpy as np
import pandas as pd
import math
import io
import re
import plotly.graph_objects as go

# ---------------------------
# Azimuth Converter - Versión limpia (solo español)
# Mejoras incluidas:
# - Código en un solo idioma (español)
# - Selector de tema (Claro/Oscuro) elegante en la barra lateral
# - CSS mejorado para móvil y botones
# - Se eliminaron variables y lógica de idioma innecesarias
# - Limpieza general y pequeños ajustes UI
# ---------------------------

# Contador de visitas (imagen)
st.markdown(
    '<img src="https://hitscounter.dev/api/hit?url=https%3A%2F%2Fpolar2xy.streamlit.app%2F&label=visitas&icon=github&color=%233dd5f3&message=&style=flat&tz=UTC">',
    unsafe_allow_html=True
)

# CSS personalizado (optimizado móvil y botones)
st.markdown("""
<style>
    /* Responsive design y mejoras de control */
    @media (max-width: 768px) {
        .main-header { font-size: 1.45rem !important; }
        .stButton>button { padding: 0.6rem 0.8rem !important; font-size: 0.95rem !important; }
    }

    .main-header {
        font-size: 2.1rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.6rem;
        font-weight: 700;
    }

    .modebar { position: absolute !important; top: 48px !important; right: 12px !important; z-index:1000 !important; }

    .point-button { background-color: #28a745 !important; color: white !important; border-radius: 8px !important; }
    .clear-points-button { background-color: #dc3545 !important; color: white !important; border-radius: 8px !important; }

    div[data-testid="stPlotlyChart"] { margin-top: 48px !important; }

    html, body, .stApp, div#root { overscroll-behavior-y: none !important; touch-action: pan-y !important; }

    .offline-indicator { position: fixed; top: 10px; right: 10px; background-color: #28a745; color: white; padding: 6px 10px; border-radius: 14px; font-size: 12px; z-index: 999; }

    div[data-testid="stDataFrame"] { overflow-x: auto; }

    @media (orientation: portrait) {
        .js-plotly-plot .plotly { height: 55vh !important; }
        .stDataFrame { height: 220px !important; }
    }
</style>
""", unsafe_allow_html=True)

# JS para evitar pull-to-refresh en dispositivos móviles
st.markdown("""
<script>
    document.addEventListener('touchstart', function(e) {
        if (window.scrollY === 0 && e.touches[0].clientY < 50) e.preventDefault();
    }, { passive: false });
    document.addEventListener('touchmove', function(e) {
        if (window.scrollY === 0 && e.touches[0].clientY < 50) e.preventDefault();
    }, { passive: false });
</script>
""", unsafe_allow_html=True)

# --- Funciones utilitarias ---

def calculate_polygon_area(coordinates):
    """Calcular área de polígono (fórmula del calzado / shoelace)."""
    if len(coordinates) < 3:
        return 0.0
    n = len(coordinates)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += coordinates[i][0] * coordinates[j][1]
        area -= coordinates[i][1] * coordinates[j][0]
    return abs(area) / 2.0


def azimuth_to_coordinates(azimuth, distance, ref_x=0.0, ref_y=0.0):
    """Convertir azimut (grados) y distancia a coordenadas X,Y con convención: Norte=0°, horario."""
    azimuth_rad = math.radians(azimuth)
    x_offset = math.sin(azimuth_rad) * distance
    y_offset = math.cos(azimuth_rad) * distance
    x = ref_x + x_offset
    y = ref_y + y_offset
    return round(x, 3), round(y, 3)


def parse_dms_to_decimal(dms_string):
    """Convertir formatos DMS o entradas móviles a grados decimales."""
    try:
        dms_string = str(dms_string).strip()
        dms_string = dms_string.replace(',', '.')
        patterns = [
            r"(\d+(?:\.\d+)?)[°d]\s*(\d+(?:\.\d+)?)[\'m]\s*(\d+(?:\.\d+)?)[\"\'s]?",
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
    return 0 <= azimuth <= 360


# --- Gráfico combinado ---

def create_multi_point_plot(single_points, results_df, ref_x, ref_y, x_coord, y_coord, bg_color='Blanco'):
    fig = go.Figure()

    # Punto referencia
    ref_text_color = 'blue' if bg_color == 'Blanco' else 'lightblue'
    fig.add_trace(go.Scatter(
        x=[ref_x], y=[ref_y], mode='markers+text', name='Referencia',
        marker=dict(color='blue', size=16, symbol='circle'), text=['REF'], textposition='bottom center',
        textfont=dict(size=14, color=ref_text_color), hovertemplate='<b>Referencia</b><br>X: %{x:.3f}<br>Y: %{y:.3f}<extra></extra>'
    ))

    single_points_area = 0.0
    if not single_points.empty:
        colors = ['red','orange','purple','brown','pink','gray','olive','cyan']
        if bg_color == 'Negro':
            colors = ['lightcoral','gold','violet','sienna','lightpink','lightgray','lightgreen','lightcyan']
        for i, (_, row) in enumerate(single_points.iterrows()):
            color = colors[i % len(colors)]
            point_name = f'P{i+1}'
            fig.add_trace(go.Scatter(
                x=[row['X']], y=[row['Y']], mode='markers+text', name=point_name,
                marker=dict(color=color, size=12, symbol='diamond'), text=[point_name], textposition='top center',
                textfont=dict(size=12, color=color), hovertemplate=f'<b>{point_name} (Ingresado)</b><br>X: %{{x:.3f}}<br>Y: %{{y:.3f}}<extra></extra>'
            ))
        if len(single_points) >= 3:
            all_x = single_points['X'].tolist(); all_y = single_points['Y'].tolist()
            all_x.append(all_x[0]); all_y.append(all_y[0])
            poly_line_color = 'green' if bg_color == 'Blanco' else 'lightgreen'
            fig.add_trace(go.Scatter(x=all_x, y=all_y, mode='lines', name='Polígono (Puntos Ingresados)',
                                     line=dict(color=poly_line_color, width=3), fill='toself', fillcolor='rgba(40,167,69,0.2)', hoverinfo='skip'))
            single_points_area = calculate_polygon_area(list(zip(single_points['X'], single_points['Y'])))

    # Punto vista previa
    if x_coord != 0 or y_coord != 0:
        preview_color = 'green' if bg_color == 'Blanco' else 'lightgreen'
        fig.add_trace(go.Scatter(x=[x_coord], y=[y_coord], mode='markers', name='Punto Actual (Vista Previa)',
                                 marker=dict(color=preview_color, size=14, symbol='x'), hovertemplate='<b>Punto Actual</b><br>X: %{x:.3f}<br>Y: %{y:.3f}<extra></extra>'))

    polygon_area = 0.0
    if not results_df.empty:
        all_x = [ref_x] + results_df['X_Coordinate'].tolist(); all_y = [ref_y] + results_df['Y_Coordinate'].tolist()
        poly_az_line_color = 'blue' if bg_color == 'Blanco' else 'lightblue'
        fig.add_trace(go.Scatter(x=all_x + [all_x[0]], y=all_y + [all_y[0]], mode='lines', name='Polígono (Azimut)',
                                 line=dict(color=poly_az_line_color, width=3), fill='toself', fillcolor='rgba(31,119,180,0.2)', hoverinfo='skip'))
        marker_color = 'red' if bg_color == 'Blanco' else 'lightcoral'
        text_color = 'black' if bg_color == 'Blanco' else 'white'
        labels = [f'A{i+1}' for i in range(len(results_df))] if len(results_df) <= 20 else None
        mode = 'markers+text' if labels is not None else 'markers'
        fig.add_trace(go.Scatter(x=results_df['X_Coordinate'], y=results_df['Y_Coordinate'], mode=mode, name='Puntos del Polígono (Azimut)',
                                 marker=dict(color=marker_color, size=10, symbol='circle'), text=labels, textposition='top center',
                                 textfont=dict(size=9, color=text_color), hovertemplate='<b>Punto A%{pointNumber}</b><br>X: %{x:.3f}<br>Y: %{y:.3f}<extra></extra>'))
        arrow_color = 'rgba(0,100,200,0.5)' if bg_color == 'Blanco' else 'rgba(173,216,230,0.5)'
        annotation_font_color = 'darkblue' if bg_color == 'Blanco' else 'lightblue'
        for i, row in results_df.iterrows():
            if i == 0:
                start_x, start_y = ref_x, ref_y
            else:
                start_x = results_df.iloc[i-1]['X_Coordinate']; start_y = results_df.iloc[i-1]['Y_Coordinate']
            fig.add_annotation(x=row['X_Coordinate'], y=row['Y_Coordinate'], ax=start_x, ay=start_y, xref='x', yref='y', axref='x', ayref='y',
                               showarrow=True, arrowhead=2, arrowsize=1, arrowwidth=1.5, arrowcolor=arrow_color, text='',
                               font=dict(size=15, color=annotation_font_color), bgcolor='rgba(0,0,0,0)', borderpad=0, standoff=5)
        polygon_area = calculate_polygon_area(list(zip([ref_x] + results_df['X_Coordinate'].tolist(), [ref_y] + results_df['Y_Coordinate'].tolist())))

    title_text = (f'Visualización Combinada | Puntos Ingresados: {len(single_points)} | Área Puntos: {single_points_area:.3f} m² '
                  f'| Puntos Polígono Azimut: {len(results_df)} | Área Azimut: {polygon_area:.3f} m²')
    plot_bgcolor = 'white' if bg_color == 'Blanco' else 'black'
    grid_color = 'rgba(200,200,200,0.5)' if bg_color == 'Blanco' else 'rgba(100,100,100,0.5)'
    font_color = 'black' if bg_color == 'Blanco' else 'white'

    fig.update_layout(title={'text': title_text, 'x': 0.5, 'xanchor': 'center', 'font': {'size': 20, 'color': font_color}},
                      xaxis_title='X (m)', yaxis_title='Y (m)', showlegend=True,
                      legend=dict(orientation='v', yanchor='top', y=1, xanchor='left', x=1.02, font=dict(color=font_color)),
                      hovermode='closest', height=900, width=1400, yaxis=dict(scaleanchor='x', scaleratio=1),
                      plot_bgcolor=plot_bgcolor, paper_bgcolor=plot_bgcolor, dragmode='pan', font=dict(color=font_color))

    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=grid_color, title_font=dict(color=font_color), tickfont=dict(color=font_color))
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=grid_color, title_font=dict(color=font_color), tickfont=dict(color=font_color))

    config = {'displayModeBar': True, 'displaylogo': False, 'modeBarButtonSize': 20, 'doubleClick': 'reset', 'scrollZoom': True,
              'toImageButtonOptions': {'format': 'png', 'filename': 'combined_plot', 'height': 900, 'width': 1400, 'scale': 2}}

    return fig, config


# --- Interfaz principal ---

def main():
    st.set_page_config(page_title='Convertidor Azimut', page_icon='🧭', layout='wide', initial_sidebar_state='auto')

    # Indicador offline
    st.markdown('<div class="offline-indicator">📱 Offline Ready</div>', unsafe_allow_html=True)

    # Estado inicial
    if 'single_points' not in st.session_state:
        st.session_state.single_points = pd.DataFrame({'X': [], 'Y': []})
    if 'batch_data' not in st.session_state:
        st.session_state.batch_data = pd.DataFrame({'Azimuth': [], 'Distance': []})

    # Sidebar: configuración y selector de tema elegante
    st.sidebar.header('⚙️ Configuración')
    ref_x = st.sidebar.number_input('Referencia X', value=1000.0, help='Coordenada X del punto de referencia')
    ref_y = st.sidebar.number_input('Referencia Y', value=1000.0, help='Coordenada Y del punto de referencia')

    tema = st.sidebar.selectbox('Tema', options=['Claro', 'Oscuro'], index=0)
    bg_color = 'Blanco' if tema == 'Claro' else 'Negro'

    st.title('🧭 Convertidor de Azimut a Coordenadas', anchor=None)
    st.markdown('Convierte medidas de azimut y distancia a coordenadas X,Y o ingresa puntos directamente.')

    azimuth_convention = 'excel'

    # Gestión de puntos
    st.header('📊 Conversión por Lotes')
    st.subheader('📍 Gestión de Puntos')

    col_btn1, col_btn2, col_btn3 = st.columns([1,1,2])
    with col_btn1:
        if st.button('➕ Agregar Punto', key='add_point'):
            if 'current_x' in st.session_state and 'current_y' in st.session_state:
                x = st.session_state.current_x; y = st.session_state.current_y
                try:
                    new_point = pd.DataFrame({'X':[x], 'Y':[y]})
                    st.session_state.single_points = pd.concat([st.session_state.single_points, new_point], ignore_index=True)
                    st.success(f'✅ ¡Punto agregado! Total puntos: {len(st.session_state.single_points)}')
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f'❌ Error al agregar punto: {str(e)}')
    with col_btn2:
        if st.button('🗑️ Limpiar Puntos', key='clear_points'):
            st.session_state.single_points = pd.DataFrame({'X':[], 'Y':[]})
            st.success('✅ ¡Todos los puntos eliminados!')
            st.experimental_rerun()
    with col_btn3:
        st.info(f'**Puntos actuales:** {len(st.session_state.single_points)}')
        if not st.session_state.single_points.empty:
            st.metric('Último Punto', f"({st.session_state.single_points.iloc[-1]['X']:.3f}, {st.session_state.single_points.iloc[-1]['Y']:.3f})")

    if len(st.session_state.single_points) >= 3:
        coordinates = list(zip(st.session_state.single_points['X'], st.session_state.single_points['Y']))
        single_points_area = calculate_polygon_area(coordinates)
        st.subheader('📐 Área del Polígono de Puntos Ingresados')
        st.metric('Área', f'{single_points_area:.3f} m²')

    if not st.session_state.single_points.empty:
        with st.expander('📋 Ver Todos los Puntos', expanded=False):
            st.dataframe(st.session_state.single_points[['X','Y']], use_container_width=True, height=200)

    # Ingreso de coordenadas
    st.subheader('📊 Ingreso de Coordenadas')
    x_coord = st.number_input('Coordenada X', value=0.0, step=0.001, format='%.3f', help='Ingresa la coordenada X del punto', key='x_input')
    st.session_state.current_x = x_coord
    y_coord = st.number_input('Coordenada Y', value=0.0, step=0.001, format='%.3f', help='Ingresa la coordenada Y del punto', key='y_input')
    st.session_state.current_y = y_coord

    if x_coord != 0 or y_coord != 0:
        st.subheader('📍 Resultados')
        col_x, col_y = st.columns(2)
        with col_x: st.metric('Coordenada X', f'{x_coord:.3f}')
        with col_y: st.metric('Coordenada Y', f'{y_coord:.3f}')
        st.write(f"**Entrada:** Coordenadas ({x_coord:.3f}, {y_coord:.3f})")
    else:
        st.info('👈 Ingresa valores de coordenadas para ver resultados')

    st.markdown('---')
    st.subheader('Carga de Datos por Lotes')
    st.subheader('Ingresar Datos')

    if not st.session_state.batch_data.empty:
        st.write('**Datos Actuales:**')
        st.dataframe(st.session_state.batch_data, use_container_width=True, height=250)

    if 'form_counter' not in st.session_state:
        st.session_state.form_counter = 0

    with st.form(f"add_entry_form_{st.session_state.form_counter}"):
        st.write('**Agregar Nueva Entrada:**')
        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            new_azimuth = st.text_input('Azimut', value='', placeholder='26 56 7.00 o 26.935', help='Formatos fáciles: 26 56 7.00 | 26-56-7.00 | 26:56:7.00 | 26.935')
        with col2:
            new_distance = st.number_input('Distancia', value=None, step=0.001, format='%.3f')
        with col3:
            submitted = st.form_submit_button('➕ Agregar Entrada')
        if submitted and new_azimuth and new_distance is not None and new_distance > 0:
            new_row = pd.DataFrame({'Azimuth':[new_azimuth], 'Distance':[new_distance]})
            st.session_state.batch_data = pd.concat([st.session_state.batch_data, new_row], ignore_index=True)
            st.session_state.form_counter += 1
            st.success('✅ ¡Entrada agregada!')
            st.experimental_rerun()

    st.markdown('---')
    col1, col2 = st.columns(2)
    with col1:
        if st.button('🗑️ Limpiar Todos los Datos'):
            st.session_state.batch_data = pd.DataFrame({'Azimuth':[], 'Distance':[]})
            st.experimental_rerun()
    with col2:
        if st.button('📝 Restablecer a Ejemplos'):
            st.session_state.batch_data = pd.DataFrame({'Azimuth': ['26 56 7.00','90-0-0','180:30:15.5','270_45_30'], 'Distance':[5.178,1.000,1.000,1.000]})
            st.experimental_rerun()

    if st.button('🔄 Convertir Todo', type='primary'):
        if not st.session_state.batch_data.empty:
            results = []
            errors = []
            current_ref_x = ref_x; current_ref_y = ref_y
            st.info('🔄 Procesando recorrido poligonal...')
            for index, row in st.session_state.batch_data.iterrows():
                try:
                    azimuth_raw = row['Azimuth']
                    if isinstance(azimuth_raw, str):
                        azimuth = parse_dms_to_decimal(azimuth_raw)
                        if azimuth is None:
                            errors.append(f"Fila {int(index)+1}: Formato de azimut inválido '{azimuth_raw}'")
                            continue
                    else:
                        azimuth = float(azimuth_raw)
                    distance = float(row['Distance'])
                    if not validate_azimuth(azimuth):
                        errors.append(f"Fila {int(index)+1}: Azimut inválido {azimuth}°")
                        continue
                    x, y = azimuth_to_coordinates(azimuth, distance, current_ref_x, current_ref_y)
                    results.append({'Row': int(index)+1, 'Azimuth_Original': str(azimuth_raw), 'Azimuth_Decimal': float(azimuth), 'Distance': float(distance), 'Reference_X': float(current_ref_x), 'Reference_Y': float(current_ref_y), 'X_Coordinate': float(x), 'Y_Coordinate': float(y)})
                    current_ref_x = x; current_ref_y = y
                except Exception as e:
                    errors.append(f"Fila {int(index)+1}: {str(e)}")
            if results:
                results_df = pd.DataFrame(results)
                st.session_state['results_df'] = results_df
                st.success(f'✅ ¡Convertidos {len(results)} puntos exitosamente!')
            if errors:
                st.error('❌ Errores encontrados:')
                for error in errors:
                    st.write(f'- {error}')
        else:
            st.warning('⚠️ No hay datos para convertir')

    # Mostrar resultados persistentes
    results_df = st.session_state.get('results_df', pd.DataFrame())
    if not results_df.empty:
        final_x = results_df.iloc[-1]['X_Coordinate']; final_y = results_df.iloc[-1]['Y_Coordinate']
        closure_error_x = abs(final_x - ref_x); closure_error_y = abs(final_y - ref_y)
        closure_error = math.sqrt(closure_error_x**2 + closure_error_y**2)
        if closure_error < 0.01:
            st.success(f'🎯 ¡El polígono CIERRA! Error: {closure_error:.6f}')
        else:
            st.error(f'⚠️ Error de cierre: {closure_error:.6f} (X: {closure_error_x:.3f}, Y: {closure_error_y:.3f})')
        coordinates = [(ref_x, ref_y)] + list(zip(results_df['X_Coordinate'], results_df['Y_Coordinate']))
        polygon_area = calculate_polygon_area(coordinates)
        st.subheader('📐 Área del Polígono Azimut')
        col1, col2 = st.columns(2)
        with col1: st.metric('Área', f'{polygon_area:.3f} m²')
        with col2: st.metric('Vértices', f"{len(results_df)}")
        if len(st.session_state.single_points) >= 3:
            single_coords = list(zip(st.session_state.single_points['X'], st.session_state.single_points['Y']))
            single_area = calculate_polygon_area(single_coords); area_diff = abs(polygon_area - single_area)
            st.subheader('📏 Comparación de Áreas')
            c1, c2, c3 = st.columns(3)
            with c1: st.metric('Área Azimut', f'{polygon_area:.3f} m²')
            with c2: st.metric('Área Puntos', f'{single_area:.3f} m²')
            with c3: st.metric('Diferencia', f'{area_diff:.3f} m²')
        displayed_df = results_df.drop(columns=['Reference_X','Reference_Y'])
        column_config = {'Row': st.column_config.NumberColumn('Pt', width='small'), 'Azimuth_Original': st.column_config.TextColumn('Azimut Original', width='medium'), 'Azimuth_Decimal': st.column_config.NumberColumn('Azimut Decimal', width='medium'), 'Distance': st.column_config.NumberColumn('Distancia', width='small'), 'X_Coordinate': st.column_config.NumberColumn('X', width='medium'), 'Y_Coordinate': st.column_config.NumberColumn('Y', width='medium')}
        st.dataframe(displayed_df, column_config=column_config, use_container_width=True, height=300)
        csv_buffer = io.StringIO(); displayed_df.to_csv(csv_buffer, index=False); csv_data = csv_buffer.getvalue()
        st.download_button(label='📥 Descargar Resultados como CSV', data=csv_data, file_name='azimuth_results.csv', mime='text/csv')
        txt_buffer = io.StringIO(); txt_buffer.write('pt,x,y\n')
        for _, row in results_df.iterrows(): txt_buffer.write(f"{int(row['Row'])},{row['X_Coordinate']:.3f},{row['Y_Coordinate']:.3f}\n")
        txt_data = txt_buffer.getvalue()
        st.download_button(label='📥 Descargar Coordenadas como TXT (pt,x,y)', data=txt_data, file_name='coordenadas.txt', mime='text/plain')

    # Visualización
    st.subheader('📈 Visualización')
    results_df = st.session_state.get('results_df', pd.DataFrame())
    try:
        fig, config = create_multi_point_plot(st.session_state.single_points, results_df, ref_x, ref_y, x_coord, y_coord, bg_color)
        st.plotly_chart(fig, use_container_width=True, config=config)
    except Exception as e:
        st.error(f'Error de visualización: {str(e)}')

    with st.expander('ℹ️ Cómo usar la visualización'):
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

if __name__ == '__main__':
    main()
