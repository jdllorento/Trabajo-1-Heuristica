import numpy as np
import random

def get_job_offsets(m, processing_times_j):
    offsets = np.zeros(m, dtype=int)
    for u in range(1, m):
        offsets[u] = offsets[u-1] + processing_times_j[u-1]
    return offsets

def find_earliest_start(job_idx, m, machines, p_times, r_date, machine_usage):
    offsets = get_job_offsets(m, p_times[job_idx])
    candidate_start = int(r_date)
    
    while True:
        feasible = True
        for u in range(m):
            m_id = machines[job_idx, u]
            op_start = candidate_start + offsets[u]
            op_end = op_start + p_times[job_idx, u]
            
            for (s, e) in machine_usage[m_id]:
                if not (op_end <= s or op_start >= e):
                    feasible = False
                    # Salto inteligente: ir al final del bloque que obstruye
                    candidate_start = max(candidate_start, int(e - offsets[u]))
                    break
            if not feasible: break
        if feasible: return candidate_start

def solve_grasp(n, m, machines, p_times, r_dates, alpha):
    """Ejecuta UNA construcción GRASP."""
    unscheduled_jobs = list(range(n))
    final_start_times = np.zeros(n, dtype=int)
    machine_usage = {k: [] for k in range(np.max(machines) + 1)}
    
    while unscheduled_jobs:
        # 1. Evaluar costos (Earliest Start Time) para candidatos
        costs = []
        for j_idx in unscheduled_jobs:
            s_j = find_earliest_start(j_idx, m, machines, p_times, r_dates[j_idx], machine_usage)
            costs.append((j_idx, s_j))
        
        # 2. Determinar límites de la RCL
        f_min = min(c[1] for c in costs)
        f_max = max(c[1] for c in costs)
        threshold = f_min + alpha * (f_max - f_min)
        
        # 3. Construir RCL
        rcl = [c for c in costs if c[1] <= threshold]
        
        # 4. Seleccionar uno al azar
        selected_job, selected_start = random.choice(rcl)
        
        # 5. Programar y actualizar
        final_start_times[selected_job] = selected_start
        offsets = get_job_offsets(m, p_times[selected_job])
        for u in range(m):
            m_id = machines[selected_job, u]
            machine_usage[m_id].append((selected_start + offsets[u], selected_start + offsets[u] + p_times[selected_job, u]))
        
        unscheduled_jobs.remove(selected_job)
        
    return final_start_times