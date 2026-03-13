import numpy as np
import time
import pandas as pd
from engine import find_earliest_start_optimized, get_job_offsets

def solve_constructive(n, m, machines, processing_times, release_dates):
    start_time_total = time.time()
    
    # 1. Ordenamos por tiempo de procesamiento
    # Calculamos la suma de duraciones por trabajo
    total_processing_times = np.sum(processing_times, axis=1)
    # Obtenemos el orden de los índices de menor a mayor duración total
    job_order = np.argsort(total_processing_times)
    
    final_start_times = np.zeros(n, dtype=int)
    machine_usage = {k: [] for k in range(np.max(machines) + 1)}
    
    # 2. Construcción de la solución
    for job_idx in job_order:
        # Buscamos el inicio más temprano
        start = find_earliest_start_optimized(
            job_idx, m, machines, processing_times, release_dates[job_idx], machine_usage
        )
        
        final_start_times[job_idx] = start
        
        # 3. Registro de ocupación
        offsets = get_job_offsets(m, processing_times[job_idx])
        for u in range(m):
            m_id = machines[job_idx, u]
            op_start = start + offsets[u]
            op_end = op_start + processing_times[job_idx, u]
            
            machine_usage[m_id].append((op_start, op_end))
            machine_usage[m_id].sort() 

    end_time_total = time.time()
    execution_ms = int((end_time_total - start_time_total) * 1000)
    
    return final_start_times, execution_ms