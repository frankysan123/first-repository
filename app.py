import streamlit as st
import numpy as np
import pandas as pd
import math
import io
import re

# To show a hit counter image in Streamlit, use markdown with unsafe_allow_html=True
st.markdown(
    '<img src="https://hitscounter.dev/api/hit?url=https%3A%2F%2Fpolar2xy.streamlit.app%2F&label=visitas&icon=github&color=%233dd5f3&message=&style=flat&tz=UTC">',
    unsafe_allow_html=True
)

# Language translations
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
        'instructions_title': '### How to Use This Application',
        'excel_compatibility': '#### 🎯 Excel Formula Compatibility',
        'excel_compatibility_text': 'This application uses your exact Excel formulas for coordinate conversion, ensuring identical results to your spreadsheet calculations.',
        'mobile_formats': '#### 📱 Mobile-Friendly Input Formats',
        'mobile_formats_text': '**Easy ways to enter azimuth without special symbols:**\n- **Spaces**: `26 56 7.00` (degrees minutes seconds)\n- **Dashes**: `26-56-7.00`\n- **Colons**: `26:56:7.00`\n- **Underscores**: `26_56_7.00`\n- **Decimal**: `26.935` (direct decimal degrees)\n- **Traditional**: `26°56\'7.00"` (if you can type symbols)',
        'single_conversion_help': '#### 📍 Single Conversion',
        'single_conversion_steps': '1. Set reference point coordinates in sidebar (default: 1000, 1000)\n2. Choose input format: Mobile-friendly DMS or Decimal\n3. Input azimuth using any easy format above\n4. Input distance from reference point\n5. View calculated X,Y coordinates (displayed to 3 decimal places)',
        'batch_conversion_help': '#### 📊 Batch Conversion & Polygon Traversal',
        'batch_conversion_steps': '1. Choose between manual entry or CSV upload\n2. For manual entry: add rows using mobile-friendly formats\n3. For CSV upload: ensure columns are named \'Azimuth\' and \'Distance\'\n4. Click "Convert All" to process all points\n5. Each point becomes the reference for the next (polygon traversal)\n6. Check polygon closure status and download results',
        'examples_title': '#### 📋 Examples',
        'mobile_example': '**Mobile-Friendly Example:**\n- **Input**: Azimuth = `26 56 7.00`, Distance = 5.178, Reference Point = (1000,1000)\n- **Result**: X = 1002.346, Y = 1004.616',
        'decimal_example': '**Decimal Example:**\n- **Input**: Azimuth = 90.0, Distance = 10, Reference Point = (0,0)\n- **Result**: X = 10.000, Y = 0.000',
        'tips_title': '#### 💡 Tips',
        'tips_text': '- Ensure azimuth values are between 0-360 degrees\n- Use consistent units for distance measurements\n- Consider your coordinate system when choosing convention\n- For surveying applications, North convention is typically used\n- All calculations are rounded to 3 decimal places for precision',
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
        'instructions_title': '### Cómo Usar Esta Aplicación',
        'excel_compatibility': '#### 🎯 Compatibilidad con Fórmulas de Excel',
        'excel_compatibility_text': 'Esta aplicación usa tus fórmulas exactas de Excel para conversión de coordenadas, asegurando resultados idénticos a tus cálculos de hoja de cálculo.',
        'mobile_formats': '#### 📱 Formatos de Entrada Amigables para Móvil',
        'mobile_formats_text': '**Formas fáciles de ingresar azimut sin símbolos especiales:**\n- **Espacios**: `26 56 7.00` (grados minutos segundos)\n- **Guiones**: `26-56-7.00`\n- **Dos puntos**: `26:56:7.00`\n- **Guiones bajos**: `26_56_7.00`\n- **Decimal**: `26.935` (grados decimales directos)\n- **Tradicional**: `26°56\'7.00"` (si puedes escribir símbolos)',
        'single_conversion_help': '#### 📍 Conversión Individual',
        'single_conversion_steps': '1. Establece coordenadas del punto de referencia en la barra lateral (por defecto: 1000, 1000)\n2. Elige formato de entrada: GMS amigable para móvil o Decimal\n3. Ingresa azimut usando cualquier formato fácil de arriba\n4. Ingresa distancia desde el punto de referencia\n5. Ve las coordenadas X,Y calculadas (mostradas con 3 decimales)',
        'batch_conversion_help': '#### 📊 Conversión por Lotes y Recorrido de Polígono',
        'batch_conversion_steps': '1. Elige entre entrada manual o carga de CSV\n2. Para entrada manual: agrega filas usando formatos amigables para móvil\n3. Para carga CSV: asegúrate que las columnas se llamen \'Azimuth\' y \'Distance\'\n4. Haz clic en "Convert All" para procesar todos los puntos\n5. Cada punto se convierte en la referencia para el siguiente (recorrido de polígono)\n6. Verifica el estado de cierre del polígono y descarga resultados',
        'examples_title': '#### 📋 Ejemplos',
        'mobile_example': '**Ejemplo Amigable para Móvil:**\n- **Entrada**: Azimut = `26 56 7.00`, Distancia = 5.178, Punto de Referencia = (1000,1000)\n- **Resultado**: X = 1002.346, Y = 1004.616',
        'decimal_example': '**Ejemplo Decimal:**\n- **Entrada**: Azimut = 90.0, Distancia = 10, Punto de Referencia = (0,0)\n- **Resultado**: X = 10.000, Y = 0.000',
        'tips_title': '#### 💡 Consejos',
        'tips_text': '- Asegúrate que los valores de azimut estén entre 0-360 grados\n- Usa unidades consistentes para medidas de distancia\n- Considera tu sistema de coordenadas al elegir convención\n- Para aplicaciones de topografía, la convención Norte se usa típicamente\n- Todos los cálculos se redondean a 3 decimales para precisión',
    }
}

def get_text(key, lang='en'):
    """Get translated text for the given key and language"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

def calculate_polygon_area(coordinates):
    """
    Calculate polygon area using the Shoelace formula
    Input: list of (x, y) coordinate tuples
    Output: area in square units
    Formula: A = ½ |Σ(xᵢyᵢ₊₁ - yᵢxᵢ₊₁)|
    """
    if len(coordinates) < 3:
        return 0.0
    
    n = len(coordinates)
    area = 0.0
    
    # Apply Shoelace formula
    for i in range(n):
        j = (i + 1) % n  # Next vertex (wrap around to 0 for last vertex)
        area += coordinates[i][0] * coordinates[j][1]  # x₁y₂ + x₂y₃ + ...
        area -= coordinates[i][1] * coordinates[j][0]  # y₁x₂ + y₂x₃ + ...
    
    return abs(area) / 2.0

def azimuth_to_coordinates(azimuth, distance, ref_x=0.0, ref_y=0.0, azimuth_convention="north"):
    """
    Convert azimuth and distance to X,Y coordinates using Excel formulas
    
    Excel formulas:
    - X coordinate: SIN(RADIANS(F7))*G7 + ref_x
    - Y coordinate: G7*COS(RADIANS(F7)) + ref_y
    Where F7=azimuth, G7=distance
    
    Parameters:
    - azimuth: angle in degrees (F7)
    - distance: distance/radius (G7)
    - ref_x, ref_y: reference point coordinates
    - azimuth_convention: not used in Excel formula, keeping for compatibility
    
    Returns:
    - x, y: calculated coordinates
    """
    # Convert azimuth to radians (RADIANS(F7))
    azimuth_rad = math.radians(azimuth)
    
    # Excel formulas exactly as provided:
    # X coordinate: SIN(RADIANS(F7))*G7
    x_offset = math.sin(azimuth_rad) * distance
    
    # Y coordinate: G7*COS(RADIANS(F7))  
    y_offset = distance * math.cos(azimuth_rad)
    
    # Add to reference point
    x = ref_x + x_offset
    y = ref_y + y_offset
    
    # Round to 3 decimal places
    return round(x, 3), round(y, 3)

def parse_dms_to_decimal(dms_string):
    """
    Convert degrees-minutes-seconds format to decimal degrees using Excel formula
    Excel formula: =(((E7/60)+D7)/60+C7)
    Where C7=degrees, D7=minutes, E7=seconds
    Supports comma as decimal separator (26°56'7,00'')
    """
    try:
        # Remove whitespace and normalize the string
        dms_string = str(dms_string).strip()
        
        # Replace comma with dot for decimal parsing
        dms_string = dms_string.replace(',', '.')
        
        # Multiple patterns for easy mobile typing:
        patterns = [
            # Traditional symbols: 26°56'7.00" or 26d56m7.00s
            r'(\d+(?:\.\d+)?)[°d]\s*(\d+(?:\.\d+)?)[\'m]\s*(\d+(?:\.\d+)?)[\"\'s]?',
            # Space separated: "26 56 7.00"
            r'^(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)$',
            # Dash separated: "26-56-7.00"
            r'^(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)$',
            # Colon separated: "26:56:7.00"
            r'^(\d+(?:\.\d+)?):(\d+(?:\.\d+)?):(\d+(?:\.\d+)?)$',
            # Underscore separated: "26_56_7.00"
            r'^(\d+(?:\.\d+)?)_(\d+(?:\.\d+)?)_(\d+(?:\.\d+)?)$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, dms_string)
            if match and len(match.groups()) == 3:
                degrees = float(match.group(1))  # C7
                minutes = float(match.group(2))  # D7
                seconds = float(match.group(3))  # E7
                
                # Excel formula: =(((E7/60)+D7)/60+C7)
                decimal_degrees = (((seconds / 60.0) + minutes) / 60.0) + degrees
                return decimal_degrees
        
        # Fallback: try to parse as a simple decimal number
        return float(dms_string.replace(',', '.'))
    except (ValueError, AttributeError):
        return None

def validate_azimuth(azimuth):
    """Validate azimuth value is within 0-360 degrees"""
    return 0 <= azimuth <= 360

def main():
    # Configure for mobile-friendly layout
    st.set_page_config(
        page_title="Azimuth Converter",
        page_icon="🧭",
        layout="wide",
        initial_sidebar_state="auto"
    )
    
    # Add offline status indicator
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
    
    # Initialize language in session state
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    
    # Language selector in sidebar
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
    
    # Keep convention for display but not used in calculation
    azimuth_convention = "excel"
    
    # Reference point settings
    st.sidebar.subheader(get_text('reference_point', lang))
    ref_x = st.sidebar.number_input(get_text('reference_x', lang), value=1000.0, help=get_text('reference_x_help', lang))
    ref_y = st.sidebar.number_input(get_text('reference_y', lang), value=1000.0, help=get_text('reference_y_help', lang))
    
    # Main interface tabs
    tab1, tab2, tab3 = st.tabs([get_text('single_conversion', lang), get_text('batch_conversion', lang), get_text('instructions', lang)])
    
    with tab1:
        st.header(get_text('single_point_conversion', lang))
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Input method selection
            input_method = st.radio(
                get_text('azimuth_input_format', lang),
                [get_text('dms_format', lang), get_text('decimal_format', lang)],
                horizontal=True
            )
            
            if input_method.startswith(get_text('dms_format', lang)[:3]):  # Check if starts with "DMS" or "GMS"
                azimuth_input = st.text_input(
                    get_text('azimuth_easy_input', lang),
                    value="",
                    placeholder=get_text('azimuth_placeholder', lang),
                    help=get_text('azimuth_help', lang)
                )
                
                if azimuth_input:
                    # Parse DMS to decimal
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
        
        with col2:
            if azimuth > 0 or distance > 0:  # Show results if any input provided
                try:
                    x, y = azimuth_to_coordinates(azimuth, distance, ref_x, ref_y, azimuth_convention)
                    
                    st.subheader(get_text('results', lang))
                    col_x, col_y = st.columns(2)
                    with col_x:
                        st.metric(get_text('x_coordinate', lang), f"{x:.3f}")
                    with col_y:
                        st.metric(get_text('y_coordinate', lang), f"{y:.3f}")
                    
                    # Simple summary line
                    st.write(f"**{get_text('input_summary', lang)}** Azimuth {azimuth:.3f}°, {get_text('distance', lang)} {distance}, {get_text('reference_point', lang)} ({ref_x}, {ref_y})")
                        
                except Exception as e:
                    st.error(f"{get_text('calculation_error', lang)} {str(e)}")
            else:
                st.info(get_text('enter_values', lang))
    
    with tab2:
        st.header("Batch Conversion")
        st.markdown("Enter multiple azimuth and distance pairs for bulk conversion.")
        
        # Initialize session state for batch data
        if 'batch_data' not in st.session_state:
            st.session_state.batch_data = pd.DataFrame({
                'Azimuth': [],
                'Distance': []
            })
        
        # Data input options
        input_method = st.radio(
            "Input Method",
            ["Manual Entry", "Upload CSV"],
            horizontal=True
        )
        
        if input_method == "Manual Entry":
            # Simple approach using form inputs for better control
            st.subheader("Enter Data")
            
            # Display current data
            if not st.session_state.batch_data.empty:
                st.write("**Current Data:**")
                st.dataframe(st.session_state.batch_data, use_container_width=True)
            
            # Initialize form counter for clearing
            if 'form_counter' not in st.session_state:
                st.session_state.form_counter = 0
                
            # Add new entry form with dynamic key to force reset
            with st.form(f"add_entry_form_{st.session_state.form_counter}"):
                st.write("**Add New Entry:**")
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    new_azimuth = st.text_input(
                        "Azimuth", 
                        value="",  # Always start empty
                        placeholder="26 56 7.00 or 26.935",
                        help="Easy mobile formats: 26 56 7.00 | 26-56-7.00 | 26:56:7.00 | 26.935"
                    )
                
                with col2:
                    new_distance = st.number_input(
                        "Distance", 
                        value=None,  # Start empty instead of 0
                        step=0.001, 
                        format="%.3f"
                    )
                
                with col3:
                    submitted = st.form_submit_button("➕ Add Entry")
                    
                if submitted and new_azimuth and new_distance is not None and new_distance > 0:
                    new_row = pd.DataFrame({
                        'Azimuth': [new_azimuth], 
                        'Distance': [new_distance]
                    })
                    st.session_state.batch_data = pd.concat([st.session_state.batch_data, new_row], ignore_index=True)
                    
                    # Increment form counter to create new form and clear inputs
                    st.session_state.form_counter += 1
                    
                    st.success("✅ Entry added!")
                    st.rerun()
            
            # Data management buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear All Data"):
                    st.session_state.batch_data = pd.DataFrame({'Azimuth': [], 'Distance': []})
                    st.rerun()
            with col2:
                if st.button("📝 Reset to Examples"):
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
        
        # Process batch conversion
        if st.button("🔄 Convert All", type="primary"):
            if not st.session_state.batch_data.empty:
                results = []
                errors = []
                
                # Start with the initial reference point
                current_ref_x = ref_x
                current_ref_y = ref_y
                
                st.info("🔄 Processing polygon traversal - each point becomes the reference for the next...")
                
                for index, row in st.session_state.batch_data.iterrows():
                    try:
                        # Parse azimuth (could be DMS or decimal)
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
                        
                        # Calculate coordinates using current reference point
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
                        
                        # CRITICAL: Update reference point for next iteration (polygon traversal)
                        current_ref_x = x
                        current_ref_y = y
                        
                    except Exception as e:
                        errors.append(f"Row {int(index) + 1}: {str(e)}")
                
                # Display results
                if results:
                    results_df = pd.DataFrame(results)
                    st.success(f"✅ Successfully converted {len(results)} points for polygon traversal")
                    
                    # Check if polygon closes (last point should equal starting reference)
                    final_x = results_df.iloc[-1]['X_Coordinate']
                    final_y = results_df.iloc[-1]['Y_Coordinate']
                    closure_error_x = abs(final_x - ref_x)
                    closure_error_y = abs(final_y - ref_y)
                    closure_error = math.sqrt(closure_error_x**2 + closure_error_y**2)
                    
                    if closure_error < 0.01:  # Within 1cm tolerance
                        st.success(f"🎯 Polygon CLOSES! Closure error: {closure_error:.6f}")
                    else:
                        st.error(f"⚠️ Polygon closure error: {closure_error:.6f} (X: {closure_error_x:.3f}, Y: {closure_error_y:.3f})")
                    
                    # Calculate polygon area
                    coordinates = [(ref_x, ref_y)]  # Start with initial reference point
                    for _, row in results_df.iterrows():
                        coordinates.append((row['X_Coordinate'], row['Y_Coordinate']))
                    
                    polygon_area = calculate_polygon_area(coordinates)
                    
                    # Display area calculation
                    st.subheader("📐 Polygon Area")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Area", f"{polygon_area:.3f} m²", help="Calculated using Shoelace formula")
                    with col2:
                        st.metric("Vertices", f"{len(results)}", help="Number of calculated points")
                    
                    st.dataframe(results_df, use_container_width=True)
                    
                    # Download results
                    csv_buffer = io.StringIO()
                    results_df.to_csv(csv_buffer, index=False)
                    csv_data = csv_buffer.getvalue()
                    
                    st.download_button(
                        label="📥 Download Results as CSV",
                        data=csv_data,
                        file_name="azimuth_to_coordinates_results.csv",
                        mime="text/csv"
                    )
                
                # Display errors if any
                if errors:
                    st.error("❌ Errors encountered:")
                    for error in errors:
                        st.write(f"- {error}")
            else:
                st.warning("⚠️ No data to convert")
    
    with tab3:
        st.header(get_text('instructions', lang).replace('ℹ️ ', ''))
        
        st.markdown(get_text('instructions_title', lang))
        
        st.markdown(get_text('excel_compatibility', lang))
        st.markdown(get_text('excel_compatibility_text', lang))
        
        st.markdown(get_text('mobile_formats', lang))
        st.markdown(get_text('mobile_formats_text', lang))
        
        st.markdown(get_text('single_conversion_help', lang))
        st.markdown(get_text('single_conversion_steps', lang))
        
        st.markdown(get_text('batch_conversion_help', lang))
        st.markdown(get_text('batch_conversion_steps', lang))
        
        st.markdown(get_text('examples_title', lang))
        st.markdown(get_text('mobile_example', lang))
        st.markdown("")
        st.markdown(get_text('decimal_example', lang))
        
        st.markdown(get_text('tips_title', lang))
        st.markdown(get_text('tips_text', lang))

if __name__ == "__main__":
    main()
        