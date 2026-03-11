import numpy as np

def find_earliest_start_optimized(job_idx, m, machines, p_times, r_date, machine_usage):
    # Calcular offsets una sola vez
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