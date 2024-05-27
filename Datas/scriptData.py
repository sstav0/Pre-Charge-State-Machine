import numpy as np
import matplotlib.pyplot as plt

def read_data(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        num_lines = len(lines) - 1  # Subtract one for the header line
        
        values = np.zeros(num_lines)
        timestamps = np.zeros(num_lines)
        
        start_time = None
        
        for i, line in enumerate(lines[1:], start=0):  # Skip the header line
            parts = line.strip().split(';')
            value = float(parts[1])
            time_ms = float(parts[2])
            
            if i == 0:
                start_time = time_ms
            
            adjusted_time = time_ms - start_time
            
            values[i] = value
            timestamps[i] = adjusted_time
        
        return values, timestamps
    
    except IOError:
        print(f"Could not open file {file_path}")
        return None, None
    

def compute_time_constant(values1, values2, timestamps1):
    look = False
    t = 0
    abs_time = 0
    inf_value = np.mean(values2)
    t_start = 0
    
    for i in range(1, len(values1)):
        if (values1[i] - values1[i-1] > 5) and not look:
            look = True
            t_start = timestamps1[i]
        
        if look:
            if 0.948 * inf_value < values1[i] < 0.952 * inf_value:
                t = (timestamps1[i] - t_start) / 3
                abs_time = timestamps1[i]
                break
    
    return t, abs_time, inf_value, t_start

def extendArray(array1, array2):
    if len(array1) > len(array2):
        array2 = np.append(array2, np.zeros(len(array1) - len(array2)))
    elif len(array2) > len(array1):
        array1 = np.append(array1, np.zeros(len(array2) - len(array1)))
    return array1, array2

def plot_data(file_path1, file_path2, mode, file_path3=None, file_path4=None):
    values1, timestamps1 = read_data(file_path1)
    values2, timestamps2 = read_data(file_path2)
    
    if mode == 'ct' or mode == 'vi' or mode=='pe': 
        values3, timestamps3 = read_data(file_path3)
        values4, timestamps4 = read_data(file_path4)
    
    if values1 is None or timestamps1 is None:
        print('No data found in the first file.')
        return
    if values2 is None or timestamps2 is None:
        print('No data found in the second file.')
        return
    
    if mode == 'ct' or mode == 'vi' or mode=='pe':
        if values3 is None or timestamps3 is None:
            print('No data found in the third file.')
            return
        if values4 is None or timestamps4 is None:
            print('No data found in the fourth file.')
            return
    
    diff_values1 = np.diff(timestamps1)
    diff_values2 = np.diff(timestamps2)
    if mode == 'ct' or mode == 'vi' or mode=='pe':
        diff_values3 = np.diff(timestamps3)
        diff_values4 = np.diff(timestamps4)
        
    filtered_values1 = diff_values1[diff_values1 < 50]
    filtered_values2 = diff_values2[diff_values2 < 50]
    if mode == 'ct' or mode == 'vi' or mode=='pe':
        filtered_values3 = diff_values3[diff_values3 < 50]
        filtered_values4 = diff_values4[diff_values4 < 50]
    
    if mode == 'ct' or mode == 'vi' or mode == 'pe':
        resolution = np.mean(np.array([np.mean(filtered_values1), np.mean(filtered_values2), np.mean(filtered_values3), np.mean(filtered_values4)]))
    else:
        resolution = np.mean(np.array([np.mean(filtered_values1), np.mean(filtered_values2)]))
    
    if mode == 'v':
        t, abs_time, inf_value, t_start = compute_time_constant(values1, values2, timestamps1)
    
    if mode == 'pe':
        values2bis, values4bis = extendArray(values2, values4)
        power1 = values2bis * values4bis
        energy1 = np.cumsum(power1) * (timestamps1[1] - timestamps1[0]) 
        
    plt.figure()
    if mode == 'ct': 
        plt.plot(timestamps1, values1, 'b', label='Main Contactor 1')
        plt.plot(timestamps2, values2, 'r', label='Main Contactor 2')
        plt.plot(timestamps3, values3, 'g', label='Bypass Contactor 1')
        plt.plot(timestamps4, values4, 'm', label='Bypass Contactor 2')
    elif mode == 'vi':
        plt.plot(timestamps1, values1, 'b-', label='Voltage Supply')
        plt.plot(timestamps2, values2, 'r-', label='Voltage Load')
        plt.plot(timestamps3, values3, 'g-', label='Current Supply')
        plt.plot(timestamps4, values4, 'm-', label='Current Load')
    elif mode == 'pe' : 
        plt.plot(timestamps4, power1, 'g--', label='Power Supply')
        plt.plot(timestamps4, energy1, 'm--', label='Energy')
    else :
        plt.plot(timestamps1, values1, 'b', label='Supply')
        plt.plot(timestamps2, values2, 'r', label='Load')
    

    
    plt.xlabel('Time (ms)')
    plt.ylabel('Value')
    plt.title('Value over Time')
    plt.legend()
    plt.grid(True)
    
    resolution_text = f'Data Resolution: {resolution:.2f} ms'
    plt.annotate(resolution_text, xy=(0.8, 0.96), xycoords='figure fraction', 
                 bbox=dict(facecolor='white', alpha=0.5), fontsize=12, fontweight='bold')
    
    if mode == 'v':
        time_constant_text = f'Time Constant (t): {t:.1f} ms\nC (for R = 200 Ω) = {(t/(1000*200))*1e6:.1f} µF'
        plt.annotate(time_constant_text, xy=(0.8, 0.9), xycoords='figure fraction', 
                     bbox=dict(facecolor='white', alpha=0.5), fontsize=12, fontweight='bold')
        
        plt.plot(t_start, 0, 'go', markersize=8, label='startTime')
        plt.text(t_start, 0, f'({t_start}, 0)', verticalalignment='top', horizontalalignment='right')
        
        plt.plot(0, inf_value, 'mo', markersize=8, label='Inf Value')
        plt.text(0, inf_value, f'(0, {inf_value:.2f})', verticalalignment='bottom', horizontalalignment='left')
        
        plt.axhline(inf_value, color=[1, 0.5, 0], linestyle='--', linewidth=2, label='Inf Value')
        plt.axvline(abs_time, color=[0.6, 0.2, 0], linestyle='--', linewidth=2, label='Abs Time')
    plt.show()
# Execution : 
folder = "23-05"
plot_data(f"{folder}/LoadVoltage.txt", f"{folder}/SupplyVoltage.txt", 'v')
plot_data(f'{folder}/LoadCurrent.txt', f'{folder}/SupplyCurrent.txt', 'c')
plot_data(f'{folder}/MainContactor1.txt', f'{folder}/MainContactor2.txt', 'ct', f'{folder}/BypassContactor1.txt', f'{folder}/BypassContactor2.txt')
# plot_data(f'{folder}/SupplyVoltage.txt', f'{folder}/LoadVoltage.txt', 'pe', f'{folder}/SupplyCurrent.txt', f'{folder}/LoadCurrent.txt')