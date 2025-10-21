import streamlit as st
import numpy as np
import pandas as pd
import math
import io
import re
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# [Mantengo todo el CSS y las traducciones existentes...]
st.markdown(
    '<img src="https://hitscounter.dev/api/hit?url=https%3A%2F%2Fpolar2xy.streamlit.app%2F&label=visitas&icon=github&color=%233dd5f3&message=&style=flat&tz=UTC">',
    unsafe_allow_html=True
)

# Custom CSS (mantengo el existente y agrego estilos para los nuevos botones)
st.markdown("""
<style>
    /* [CSS existente mantenido...] */
    
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

# [Mantengo todas las funciones existentes: TRANSLATIONS, calculate_polygon_area, azimuth_to_coordinates, parse_dms_to_decimal, validate_azimuth...]

# Nueva función para crear gráfica con múltiples puntos
def create_multi_point_plot(points_data, ref_x, ref_y, lang='en'):
    """Create interactive plot for multiple points"""
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
    
    # All calculated points
    if not points_data.empty:
        colors = ['red', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        
        for i, (_, row) in enumerate(points_data.iterrows()):
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
                hovertemplate=f'<b>{point_name}</b><br>X: %{{x:.3f}}<br>Y: %{{y:.3f}}<br>Azimuth: {row["Azimuth"]:.2f}°<br>Distance: {row["Distance"]:.3f}<extra></extra>'
            ))
            
            # Line from reference to point
            fig.add_trace(go.Scatter(
                x=[ref_x, row['X']],
                y=[ref_y, row['Y']],
                mode='lines',
                name=f'{point_name} Line',
                line=dict(color=color, width=2, dash='dash'),
                showlegend=False,
                hovertemplate=f'<b>{point_name}</b><br>Distance: {row["Distance"]:.3f}<extra></extra>'
            ))
            
            # Arrow annotation
            fig.add_annotation(
                x=row['X'],
                y=row['Y'],
                ax=ref_x,
                ay=ref_y,
                xref='x',
                yref='y',
                axref='x',
                ayref='y',
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor=color
            )
    
    fig.update_layout(
        title={
            'text': f'Multiple Points Visualization | Total Points: {len(points_data)}',
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
        'modeBarButtonSize': 20,
        'doubleClick': 'reset',
        'scrollZoom': True
    }
    
    return fig, config

def main():
    st.set_page_config(
        page_title="Azimuth Converter",
        page_icon="🧭",
        layout="wide",
        initial_sidebar_state="auto"
    )
    
    # [Mantengo el código de offline indicator y configuración inicial...]
    
    # Initialize session state for points
    if 'single_points' not in st.session_state:
        st.session_state.single_points = pd.DataFrame({
            'Azimuth': [],
            'Distance': [],
            'X': [],
            'Y': []
        })
    
    # [Sidebar y configuración de idioma igual...]
    
    # Reference point (sidebar)
    st.sidebar.subheader(get_text('reference_point', lang))
    ref_x = st.sidebar.number_input(get_text('reference_x', lang), value=1000.0, help=get_text('reference_x_help', lang))
    ref_y = st.sidebar.number_input(get_text('reference_y', lang), value=1000.0, help=get_text('reference_y_help', lang))
    
    # Tabs
    tab1, tab2 = st.tabs([get_text('single_conversion', lang), get_text('batch_conversion', lang)])
    
    with tab1:
        st.header(get_text('single_point_conversion', lang))
        
        # Add points management section
        st.subheader("📍 Points Management")
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            if st.button("➕ Add Point", key="add_point", help="Calculate and add current point to visualization", 
                        use_container_width=True, type="primary"):
                # Get current inputs
                if 'current_azimuth' in st.session_state and st.session_state.current_azimuth > 0:
                    azimuth = st.session_state.current_azimuth
                    distance = st.session_state.current_distance if 'current_distance' in st.session_state else 0
                    
                    try:
                        x, y = azimuth_to_coordinates(azimuth, distance, ref_x, ref_y, azimuth_convention)
                        
                        # Add to points data
                        new_point = pd.DataFrame({
                            'Azimuth': [azimuth],
                            'Distance': [distance],
                            'X': [x],
                            'Y': [y]
                        })
                        
                        st.session_state.single_points = pd.concat([st.session_state.single_points, new_point], ignore_index=True)
                        st.success(f"✅ Point added! Total points: {len(st.session_state.single_points)}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error adding point: {str(e)}")
        
        with col_btn2:
            if st.button("🗑️ Clear Points", key="clear_points", help="Remove all points from visualization",
                        use_container_width=True):
                st.session_state.single_points = pd.DataFrame({
                    'Azimuth': [], 'Distance': [], 'X': [], 'Y': []
                })
                st.success("✅ All points cleared!")
                st.rerun()
        
        with col_btn3:
            st.info(f"**Current points:** {len(st.session_state.single_points)}")
            if not st.session_state.single_points.empty:
                st.metric("Last Point", f"({st.session_state.single_points.iloc[-1]['X']:.3f}, {st.session_state.single_points.iloc[-1]['Y']:.3f})")
        
        # Show points table if any
        if not st.session_state.single_points.empty:
            with st.expander("📋 View All Points", expanded=False):
                st.dataframe(st.session_state.single_points[['Azimuth', 'Distance', 'X', 'Y']], 
                           use_container_width=True, height=200)
        
        # Single point calculation section
        col1, col2 = st.columns([1, 1.4])
        
        with col1:
            # [Mantengo toda la lógica de entrada de azimuth y distance...]
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
                    help=get_text('azimuth_help', lang),
                    key="azimuth_input"
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
                        st.session_state.current_azimuth = azimuth
                else:
                    azimuth = 0.0
                    if 'current_azimuth' in st.session_state:
                        del st.session_state.current_azimuth
            else:
                azimuth = st.number_input(
                    get_text('azimuth_decimal', lang),
                    min_value=0.0,
                    max_value=360.0,
                    value=0.0,
                    step=0.001,
                    format="%.3f",
                    help=get_text('azimuth_decimal_help', lang),
                    key="azimuth_decimal"
                )
                st.session_state.current_azimuth = azimuth
            
            distance = st.number_input(
                get_text('distance', lang),
                min_value=0.0,
                value=1.0,
                step=0.001,
                format="%.3f",
                help=get_text('distance_help', lang),
                key="distance_input"
            )
            st.session_state.current_distance = distance
            
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
                    
                    if not st.session_state.single_points.empty:
                        # Show multi-point visualization
                        fig, config = create_multi_point_plot(st.session_state.single_points, ref_x, ref_y, lang)
                        # Add current calculation as preview
                        fig.add_trace(go.Scatter(
                            x=[x],
                            y=[y],
                            mode='markers',
                            name='Current Point (Preview)',
                            marker=dict(color='green', size=14, symbol='x'),
                            hovertemplate='<b>Current Point</b><br>X: %{x:.3f}<br>Y: %{y:.3f}<br>Azimuth: {:.2f}°<br>Distance: {:.3f}<extra></extra>'.format(azimuth, distance)
                        ))
                    else:
                        # Show single point visualization
                        fig, config = create_single_point_plot(ref_x, ref_y, x, y, azimuth, distance, lang)
                    
                    st.plotly_chart(fig, use_container_width=True, config=config)
                except Exception as e:
                    st.error(f"Visualization error: {str(e)}")
            else:
                st.info("👈 Enter values to see visualization")
    
    # [Mantengo la pestaña 2 (batch conversion) sin cambios...]

if __name__ == "__main__":
    main()
