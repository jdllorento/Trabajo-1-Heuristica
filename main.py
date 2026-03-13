import os
import time
import re
import pandas as pd
from read_data import read_instance, evaluate_schedule
from constructive import solve_constructive
from GRASP import solve_grasp
from noise import solve_noise

def natural_sort_key(s):
    """Ordenamiento lógico (1, 2, 10 en lugar de 1, 10, 2)"""
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]

def main():
    # ==========================================================
    # PARAMETROS DE CONTROL Y CONSTANTES
    # ==========================================================
    STUDENT_NAME = "JuanLlorente"
    INSTANCES_DIR = "NWJSSP Instances"
    
    # OPCIONES: "constructivo", "GRASP", "noise" o "todos"
    ALGO_TO_RUN = "noise"
    
    # Parámetros GRASP
    NSOL_GRASP = 20
    ALPHA = 0.1

    # Parámetros Noise
    NSOL_NOISE = 20
    NOISE_LEVEL = 0.2
    # ==========================================================

    # Preparar lista de archivos
    if not os.path.exists(INSTANCES_DIR):
        print(f"Error: No se encuentra la carpeta {INSTANCES_DIR}")
        return

    all_files = [f for f in os.listdir(INSTANCES_DIR) if f.endswith('.txt')]
    all_files.sort(key=natural_sort_key)
    
    # Inicializar solo el escritor necesario
    writers = {}
    selected_algos = ["constructivo", "GRASP", "noise"] if ALGO_TO_RUN == "todos" else [ALGO_TO_RUN]
    
    for algo in selected_algos:
        filename = f"NWJSSP_{STUDENT_NAME}_{algo}.xlsx"
        writers[algo] = pd.ExcelWriter(filename, engine='xlsxwriter')

    print(f"Ejecutando algoritmo: {ALGO_TO_RUN.upper()}")
    print("-" * 50)

    try:
        for instance_file in all_files:
            file_path = os.path.join(INSTANCES_DIR, instance_file)
            
            # Pre-lectura de dimensiones para filtro
            with open(file_path, 'r') as f:
                line = f.readline().split()
                if not line: continue
                n_jobs = int(line[0])
                n_machines = int(line[1])
            
            # No ejecutar las instancias más grandes
            if n_jobs > 100:
                continue

            n, m, machines, p_times, r_dates = read_instance(file_path)
            sheet_name = instance_file[:31]

            # --- BLOQUE EJECUCIÓN CONSTRUCTIVO ---
            if "constructivo" in selected_algos:
                st_c, dur_c = solve_constructive(n, m, machines, p_times, r_dates)
                _, z_c = evaluate_schedule(st_c, n, m, machines, p_times, r_dates)
                pd.DataFrame([[z_c, dur_c], list(st_c)]).to_excel(writers["constructivo"], sheet_name=sheet_name, index=False, header=False)
                print(f"[{instance_file}] Constructivo -> Z: {z_c} | Tiempo: {dur_c}ms | Factible: {_}")

            # --- BLOQUE EJECUCIÓN GRASP ---
            if "GRASP" in selected_algos:
                t_ini_g = time.time()
                best_z_g, best_st_g = float('inf'), None
                
                for _ in range(NSOL_GRASP):
                    st_g = solve_grasp(n, m, machines, p_times, r_dates, ALPHA)
                    _, z_g = evaluate_schedule(st_g, n, m, machines, p_times, r_dates)
                    if z_g < best_z_g:
                        best_z_g, best_st_g = z_g, st_g
                
                dur_g = int((time.time() - t_ini_g) * 1000)
                pd.DataFrame([[best_z_g, dur_g], list(best_st_g)]).to_excel(writers["GRASP"], sheet_name=sheet_name, index=False, header=False)
                print(f"[{instance_file}] GRASP        -> Z: {best_z_g} | Tiempo: {dur_g}ms | Factible: {_}")

            # --- BLOQUE EJECUCIÓN NOISE ---
            if "noise" in selected_algos:
                t_ini_n = time.time()
                best_z_n, best_st_n = float('inf'), None
                
                for _ in range(NSOL_NOISE):
                    st_n = solve_noise(n, m, machines, p_times, r_dates, NOISE_LEVEL)
                    _, z_n = evaluate_schedule(st_n, n, m, machines, p_times, r_dates)
                    if z_n < best_z_n:
                        best_z_n, best_st_n = z_n, st_n
                
                dur_n = int((time.time() - t_ini_n) * 1000)
                pd.DataFrame([[best_z_n, dur_n], list(best_st_n)]).to_excel(writers["noise"], sheet_name=sheet_name, index=False, header=False)
                print(f"[{instance_file}] Noise        -> Z: {best_z_n} | Tiempo: {dur_n}ms | Factible: {_}")

    finally:
        # Cerrar solo los escritores que se abrieron
        for w in writers.values():
            w.close()
        print("-" * 50)
        print("Proceso finalizado. Archivos Excel actualizados.")

if __name__ == "__main__":
    main()