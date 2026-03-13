import numpy as np
import random
from engine import find_earliest_start_optimized, get_job_offsets

def solve_noise(n, m, machines, p_times, r_dates, noise_level=0.15):
    # 1. Perturbación de datos para definir el orden (SPT con Ruido)
    # Solo usamos el ruido para decidir el orden
    noisy_p_times = p_times * (1 + np.random.uniform(-noise_level, noise_level, size=p_times.shape))
    priority_values = np.sum(noisy_p_times, axis=1)
    job_order = np.argsort(priority_values)
    
    final_starts = np.zeros(n, dtype=int)
    machine_usage = {k: [] for k in range(np.max(machines) + 1)}
    
    # 2. Construcción siguiendo el orden perturbado
    for job_idx in job_order:
        # Buscamos el inicio más temprano en los datos sin ruido
        start = find_earliest_start_optimized(
            job_idx, m, machines, p_times, r_dates[job_idx], machine_usage
        )
        final_starts[job_idx] = start
        
        # 3. Registro de ocupación
        offsets = get_job_offsets(m, p_times[job_idx])
        for u in range(m):
            m_id = machines[job_idx, u]
            op_start = start + offsets[u]
            op_end = op_start + p_times[job_idx, u]
            
            machine_usage[m_id].append((op_start, op_end))
            machine_usage[m_id].sort()
            
    return final_starts