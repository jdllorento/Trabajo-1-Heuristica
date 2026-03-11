import numpy as np
import time
import pandas as pd

def get_job_offsets(m, processing_times_j):
    """Calcula cuánto tiempo después del inicio del trabajo empieza cada operación."""
    offsets = np.zeros(m)
    for u in range(1, m):
        offsets[u] = offsets[u-1] + processing_times_j[u-1]
    return offsets

def solve_constructive(n, m, machines, processing_times, release_dates):
    start_time_total = time.time()
    
    # Ordenar trabajos por release date (regla de despacho simple)
    job_order = np.argsort(release_dates)
    
    # Tiempos de inicio finales para cada trabajo
    final_start_times = np.zeros(n, dtype=int)
    
    # Registro de ocupación de máquinas: lista de (inicio, fin) por máquina
    machine_usage = {k: [] for k in range(np.max(machines) + 1)}
    
    for job_idx in job_order:
        offsets = get_job_offsets(m, processing_times[job_idx])
        job_r = release_dates[job_idx]
        
        # Intentar iniciar en su release date e ir incrementando hasta que sea factible
        candidate_start = job_r
        feasible = False
        
        while not feasible:
            feasible = True
            for u in range(m):
                m_id = machines[job_idx, u]
                op_start = candidate_start + offsets[u]
                op_end = op_start + processing_times[job_idx, u]
                
                # Verificar colisión con cualquier trabajo ya programado en esta máquina
                for (s, e) in machine_usage[m_id]:
                    if not (op_end <= s or op_start >= e):
                        feasible = False
                        # Si hay colisión, movemos el candidato al fin del bloque que estorba
                        candidate_start = max(candidate_start, e - offsets[u])
                        break
                if not feasible: break
        
        # Registrar tiempos de inicio y actualizar uso de máquinas
        final_start_times[job_idx] = candidate_start
        for u in range(m):
            m_id = machines[job_idx, u]
            op_start = candidate_start + offsets[u]
            op_end = op_start + processing_times[job_idx, u]
            machine_usage[m_id].append((op_start, op_end))
            
    end_time_total = time.time()
    execution_ms = int((end_time_total - start_time_total) * 1000)
    
    return final_start_times, execution_ms

def save_to_excel(filename, instance_name, z, exec_time, start_times):
    """Genera el archivo Excel con el formato del Anexo 3."""
    # Fila 1: Z y tiempo de cómputo [cite: 80]
    # Fila 2: Tiempos de inicio de cada trabajo [cite: 81]
    data = [[z, exec_time], list(start_times)]
    df = pd.DataFrame(data)
    
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=instance_name, index=False, header=False)