import numpy as np

def find_earliest_start_optimized(job_idx, m, machines, p_times, r_date, machine_usage):
    offsets = np.zeros(m, dtype=int)
    for u in range(1, m):
        offsets[u] = offsets[u-1] + p_times[job_idx, u-1]
    
    candidate_start = int(r_date)
    
    while True:
        clash = False
        for u in range(m):
            m_id = machines[job_idx, u]
            op_start = candidate_start + offsets[u]
            op_end = op_start + p_times[job_idx, u]
            
            # Revisar colisiones en la máquina m_id
            for (s, e) in machine_usage[m_id]:
                if not (op_end <= s or op_start >= e):
                    # Si hay choque, saltamos al final del intervalo que estorba
                    candidate_start = max(candidate_start, int(e - offsets[u]))
                    clash = True
                    break
            if clash: break
        
        if not clash:
            return candidate_start
        

def get_job_offsets(m, processing_times_j):
    """Calcula los desplazamientos fijos de cada operación respecto al inicio."""
    offsets = np.zeros(m, dtype=int)
    for u in range(1, m):
        offsets[u] = offsets[u-1] + processing_times_j[u-1]
    return offsets

def calculate_lower_bound(p_times, r_dates):
    """
    Calcula la cota inferior para el Total Flow Time en NWJSSP.
    LB = Sumatoria de (Fecha de liberación + Suma de tiempos de proceso por trabajo).
    """
    total_processing_per_job = np.sum(p_times, axis=1)
    min_completion_times = r_dates + total_processing_per_job
    return int(np.sum(min_completion_times))