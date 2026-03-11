import os
import time
import re
import pandas as pd
from read_data import read_instance, evaluate_schedule
from constructive import solve_constructive
from GRASP import solve_grasp
from noise import solve_noise

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def main():
    # PARAMETROS CONSTANTES (Anexo 4)
    STUDENT_NAME = "JuanLlorente"
    INSTANCES_DIR = "NWJSSP Instances"
    NSOL_GRASP = 40  # Ajustado para velocidad en Tai
    NSOL_NOISE = 40
    ALPHA = 0.1
    NOISE_LEVEL = 0.2
    
    # Preparar archivos
    all_files = [f for f in os.listdir(INSTANCES_DIR) if f.endswith('.txt')]
    all_files.sort(key=natural_sort_key)
    
    writers = {
        "constructivo": pd.ExcelWriter(f"NWJSSP_{STUDENT_NAME}_constructivo.xlsx", engine='xlsxwriter'),
        "GRASP": pd.ExcelWriter(f"NWJSSP_{STUDENT_NAME}_GRASP.xlsx", engine='xlsxwriter'),
        "Noise": pd.ExcelWriter(f"NWJSSP_{STUDENT_NAME}_Noise.xlsx", engine='xlsxwriter')
    }

    try:
        for instance_file in all_files:
            file_path = os.path.join(INSTANCES_DIR, instance_file)
            
            # Leer dimensiones primero para decidir si procesar
            with open(file_path, 'r') as f:
                line = f.readline().split()
                if not line: continue
                n_jobs = int(line[0])
            
            # FILTRO DE SEGURIDAD: Si la instancia es > 100, saltar (o el límite que prefieras)
            if n_jobs > 100:
                print(f"--- Saltando {instance_file} (Tamaño {n_jobs} es muy grande para ejecución rápida) ---")
                continue

            print(f"\n>>> Procesando: {instance_file} ({n_jobs} trabajos)")
            n, m, machines, p_times, r_dates = read_instance(file_path)
            sheet_name = instance_file[:31]

            # 1. Ejecutar Constructivo
            st, dur = solve_constructive(n, m, machines, p_times, r_dates)
            _, z = evaluate_schedule(st, n, m, machines, p_times, r_dates)
            pd.DataFrame([[z, dur], list(st)]).to_excel(writers["constructivo"], sheet_name=sheet_name, index=False, header=False)
            print(f"  Constructivo: Z={z}")

            # 2. Ejecutar GRASP
            t_ini = time.time()
            best_z, best_st = float('inf'), None
            for _ in range(NSOL_GRASP):
                st = solve_grasp(n, m, machines, p_times, r_dates, ALPHA)
                _, z = evaluate_schedule(st, n, m, machines, p_times, r_dates)
                if z < best_z: best_z, best_st = z, st
            dur = int((time.time() - t_ini) * 1000)
            pd.DataFrame([[best_z, dur], list(best_st)]).to_excel(writers["GRASP"], sheet_name=sheet_name, index=False, header=False)
            print(f"  GRASP:        Z={best_z} ({dur}ms)")

            # 3. Ejecutar Noise
            t_ini = time.time()
            best_z, best_st = float('inf'), None
            for _ in range(NSOL_NOISE):
                st = solve_noise(n, m, machines, p_times, r_dates, NOISE_LEVEL)
                _, z = evaluate_schedule(st, n, m, machines, p_times, r_dates)
                if z < best_z: best_z, best_st = z, st
            dur = int((time.time() - t_ini) * 1000)
            pd.DataFrame([[best_z, dur], list(best_st)]).to_excel(writers["Noise"], sheet_name=sheet_name, index=False, header=False)
            print(f"  Noise:        Z={best_z} ({dur}ms)")

    finally:
        for w in writers.values(): w.close()
        print("\nTodos los archivos Excel han sido guardados.")

if __name__ == "__main__":
    main()