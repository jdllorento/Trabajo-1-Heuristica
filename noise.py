import numpy as np
import random
from engine import find_earliest_start_optimized

def solve_noise(n, m, machines, p_times, r_dates, noise_level=0.15):
    unscheduled = list(range(n))
    # El ruido influye en el orden de selección de los trabajos
    # Mezclamos un poco el orden basado en release dates con ruido
    noisy_r_dates = [r + random.uniform(-r, r) * noise_level if r > 0 else random.uniform(0, 10) for r in r_dates]
    job_order = np.argsort(noisy_r_dates)
    
    final_starts = np.zeros(n, dtype=int)
    machine_usage = {k: [] for k in range(np.max(machines) + 1)}
    
    for job_idx in job_order:
        start = find_earliest_start_optimized(job_idx, m, machines, p_times, r_dates[job_idx], machine_usage)
        final_starts[job_idx] = start
        
        # Registrar ocupación
        curr = start
        for u in range(m):
            m_id = machines[job_idx, u]
            p_t = p_times[job_idx, u]
            machine_usage[m_id].append((curr, curr + p_t))
            machine_usage[m_id].sort() # Mantener ordenado para la optimización
            curr += p_t
            
    return final_starts