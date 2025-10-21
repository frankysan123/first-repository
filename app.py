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
            
            fig.add_trace(go.Scatter(
                x=[ref_x, row['X']],
                y=[ref_y, row['Y']],
                mode='lines',
                name=f'{point_name} Línea',
                line=dict(color=color, width=2, dash='dash'),
                showlegend=False,
                hovertemplate=f'<b>{point_name}</b><br>X: %{{x:.3f}}<br>Y: %{{y:.3f}}<extra></extra>'
            ))
            
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
            
            # Add arrows to indicate direction
            for i in range(len(single_points)):
                start_x = single_points.iloc[i]['X']
                start_y = single_points.iloc[i]['Y']
                next_i = (i + 1) % len(single_points)  # Next point, looping back to 0
                end_x = single_points.iloc[next_i]['X']
                end_y = single_points.iloc[next_i]['Y']
                
                fig.add_annotation(
                    x=end_x,
                    y=end_y,
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
                    arrowcolor='rgba(40, 167, 69, 0.5)',  # Match line color
                    text="",
                    font=dict(size=15, color='darkgreen'),
                    bgcolor='rgba(0,0,0,0)',
                    borderpad=0,
                    standoff=5
                )
            
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
    title_text = (f'Visualización Combinada | Puntos Ingresados: {len(single_points)} '
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
