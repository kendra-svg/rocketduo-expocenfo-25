from datetime import datetime, timedelta

def calcular_fechas(hora_str, dias, duracion_dias):
    hoy = datetime.now()

    # Separar la hora y minutos de la cadena "HH:MM"
    hora, minuto = map(int, hora_str.split(":"))

    # CASO 1: el medicamento es diario ("todos")
    if "todos" in dias:
        fecha_inicio = hoy.date()  # se toma hoy como inicio
        # Si la hora ya pasó hoy, el primer recordatorio será mañana
        if hoy.hour > hora or (hoy.hour == hora and hoy.minute >= minuto):
            fecha_inicio += timedelta(days=1)

    # CASO 2: el medicamento se toma solo en días específicos
    else:
        dias_semana = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        indice_hoy = hoy.weekday()  # lunes=0, domingo=6
        fecha_inicio = None

        # Buscar el próximo día válido dentro de los próximos 7 días
        for i in range(7):
            dia_candidato = (indice_hoy + i) % 7  # índice del día futuro

            if dias_semana[dia_candidato] in dias:  # si el día está en la lista

                fecha_candidata = hoy + timedelta(days=i)  # calcular la fecha real

                # Si es hoy pero la hora ya pasó, continuar al siguiente día
                if i == 0 and (hoy.hour > hora or (hoy.hour == hora and hoy.minute >= minuto)):
                    continue

                fecha_inicio = fecha_candidata.date()  # asignar fecha de inicio

                break  # se sale al encontrar el primer día válido

    # Calcular fecha_fin si el tratamiento tiene duración limitada
    if duracion_dias > 0:
        fecha_fin = fecha_inicio + timedelta(days=duracion_dias - 1)
        fecha_fin = fecha_fin.strftime("%Y-%m-%d")
    else:
        fecha_fin = 0  # tratamiento permanente

    # Devolver fecha en formato "YYYY-MM-DD" y fecha_fin
    return fecha_inicio.strftime("%Y-%m-%d"), fecha_fin