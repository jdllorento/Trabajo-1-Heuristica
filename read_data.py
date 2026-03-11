import numpy as np
import os

def read_instance(file_path):
    """
    Lee una instancia del problema desde un archivo txt.
    Retorna n, m, matriz de máquinas, matriz de tiempos de procesamiento y tiempos de liberación.
    """
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Primera línea: n (trabajos) y m (máquinas)
    n, m = map(int, lines[0].strip().split())
    
    machines = np.zeros((n, m), dtype=int)
    processing_times = np.zeros((n, m), dtype=int)
    release_dates = np.zeros(n, dtype=int)
    
    for i in range(n):
        # Leer la línea del trabajo i (índice i+1 en el archivo)
        data = list(map(int, lines[i+1].strip().split()))
        
        # Extraer pares (máquina, tiempo)
        for j in range(m):
            machines[i, j] = data[2*j]
            processing_times[i, j] = data[2*j + 1]
            
        # El último valor es el release date
        release_dates[i] = data[-1]
        
    return n, m, machines, processing_times, release_dates

def evaluate_schedule(start_times, n, m, machines, processing_times, release_dates):
    """
    Evalúa una solución dada por los tiempos de inicio de cada trabajo.
    Retorna (is_feasible, total_flow_time).
    """
    is_feasible = True
    total_flow_time = 0
    
    # Estructura para revisar solapamientos en las máquinas.
    # Guardaremos una lista de intervalos (inicio, fin) por cada máquina.
    machine_intervals = {k: [] for k in range(np.max(machines) + 1)}
    
    for i in range(n):
        # Restricción: El trabajo no puede iniciar antes de su release date
        if start_times[i] < release_dates[i]:
            return False, float('inf')
        
        current_time = start_times[i]
        
        for j in range(m):
            machine = machines[i, j]
            p_time = processing_times[i, j]
            
            start_op = current_time
            end_op = current_time + p_time
            
            # Revisar solapamientos en esta máquina
            for (s, e) in machine_intervals[machine]:
                if not (end_op <= s or start_op >= e): # Hay solapamiento
                    return False, float('inf')
            
            # Registrar la operación en la máquina
            machine_intervals[machine].append((start_op, end_op))
            
            # Avanzar el tiempo para la siguiente operación (No-Wait)
            current_time = end_op
            
        # El tiempo de finalización del trabajo i es el current_time tras su última operación
        completion_time = current_time
        total_flow_time += completion_time
        
    return is_feasible, total_flow_time