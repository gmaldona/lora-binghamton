import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from math import radians, sin, cos, sqrt, atan2
from scipy import stats

# stolen from stack overflow https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
def haversine_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    R = 6371
    return R * c * 3280.84

def create_lora_plots(file_path):
    origin_lat = 42.08738732
    origin_lon = -75.96806808
    df = pd.read_csv(file_path)
    
    #calculate distances from origin in feet
    df['Distance (feet)'] = df.apply(lambda row: haversine_distance(
        origin_lat, origin_lon, row['Latitude'], row['Longitude']
    ), axis=1)
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    
    #distance vs RSSI
    df_clean_rssi = df.dropna(subset=['Average Area RSSI'])
    #color coding based on RSSI values
    scatter1 = ax1.scatter(df_clean_rssi['Distance (feet)'], df_clean_rssi['Average Area RSSI'], 
                           c=df_clean_rssi['Average Area RSSI'], cmap='coolwarm', 
                           norm=plt.Normalize(vmin=df_clean_rssi['Average Area RSSI'].min(), 
                                              vmax=df_clean_rssi['Average Area RSSI'].max()))
    ax1.set_title('Distance vs RSSI')
    ax1.set_xlabel('Distance (feet)')
    ax1.set_ylabel('RSSI')
    plt.colorbar(scatter1, ax=ax1, label='RSSI Value')
    
    #calculate and display correlation for distance vs RSSI
    corr_dist_rssi, p_dist_rssi = stats.pearsonr(df_clean_rssi['Distance (feet)'], df_clean_rssi['Average Area RSSI'])
    ax1.text(0.05, 0.95, f'Correlation: {corr_dist_rssi:.3f}\n', 
             transform=ax1.transAxes, verticalalignment='top')
    
    #distance vs SNR
    df_clean_snr = df.dropna(subset=['Average Area SNR'])
    #color coding based on SNR values
    scatter2 = ax2.scatter(df_clean_snr['Distance (feet)'], df_clean_snr['Average Area SNR'], 
                           c=df_clean_snr['Average Area SNR'], cmap='coolwarm', 
                           norm=plt.Normalize(vmin=df_clean_snr['Average Area SNR'].min(), 
                                              vmax=df_clean_snr['Average Area SNR'].max()))
    ax2.set_title('Distance vs SNR')
    ax2.set_xlabel('Distance (feet)')
    ax2.set_ylabel('SNR')
    plt.colorbar(scatter2, ax=ax2, label='SNR Value')
    
    #calculate and display correlation for distance vs SNR
    corr_dist_snr, p_dist_snr = stats.pearsonr(df_clean_snr['Distance (feet)'], df_clean_snr['Average Area SNR'])
    ax2.text(0.05, 0.95, f'Correlation: {corr_dist_snr:.3f}\n', 
             transform=ax2.transAxes, verticalalignment='top')
    
    #elevation vs RSSI
    df_clean_elev_rssi = df.dropna(subset=['Elevation (ft)', 'Average Area RSSI'])
    #color coding based on elevation
    scatter3 = ax3.scatter(df_clean_elev_rssi['Elevation (ft)'], df_clean_elev_rssi['Average Area RSSI'], 
                           c=df_clean_elev_rssi['Elevation (ft)'], cmap='coolwarm', 
                           norm=plt.Normalize(vmin=df_clean_elev_rssi['Elevation (ft)'].min(), 
                                              vmax=df_clean_elev_rssi['Elevation (ft)'].max()))
    ax3.set_title('Elevation vs RSSI')
    ax3.set_xlabel('Elevation (feet)')
    ax3.set_ylabel('RSSI')
    plt.colorbar(scatter3, ax=ax3, label='Elevation')
    
    #calculate and display correlation for elevation vs RSSI
    corr_elev_rssi, p_elev_rssi = stats.pearsonr(df_clean_elev_rssi['Elevation (ft)'], df_clean_elev_rssi['Average Area RSSI'])
    ax3.text(0.05, 0.95, f'Correlation: {corr_elev_rssi:.3f}\n', 
             transform=ax3.transAxes, verticalalignment='top')
    
    #elevation vs SNR
    df_clean_elev_snr = df.dropna(subset=['Elevation (ft)', 'Average Area SNR'])
    #color coding based on elevation
    scatter4 = ax4.scatter(df_clean_elev_snr['Elevation (ft)'], df_clean_elev_snr['Average Area SNR'], 
                           c=df_clean_elev_snr['Elevation (ft)'], cmap='coolwarm', 
                           norm=plt.Normalize(vmin=df_clean_elev_snr['Elevation (ft)'].min(), 
                                              vmax=df_clean_elev_snr['Elevation (ft)'].max()))
    ax4.set_title('Elevation vs SNR')
    ax4.set_xlabel('Elevation (feet)')
    ax4.set_ylabel('SNR')
    plt.colorbar(scatter4, ax=ax4, label='Elevation')
    
    #calculate and display correlation for elevation vs SNR
    corr_elev_snr, p_elev_snr = stats.pearsonr(df_clean_elev_snr['Elevation (ft)'], df_clean_elev_snr['Average Area SNR'])
    ax4.text(0.05, 0.95, f'Correlation: {corr_elev_snr:.3f}\n', 
             transform=ax4.transAxes, verticalalignment='top')
    
    ax1.grid(visible=True, which='both', linestyle=':', linewidth=0.7)
    ax2.grid(visible=True, which='both', linestyle=':', linewidth=0.7)
    ax3.grid(visible=True, which='both', linestyle=':', linewidth=0.7)
    ax4.grid(visible=True, which='both', linestyle=':', linewidth=0.7)

    
    plt.tight_layout()
    plt.savefig('lora_signal_plots_colored.png', dpi=300)
    plt.close()

create_lora_plots('LoRa Binghamton - HELTEC LoRa 32 - Map Plot(1).csv')