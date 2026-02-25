from fluprodia import FluidPropertyDiagram
import matplotlib.pyplot as plt
import numpy as np
from CoolProp.CoolProp import PropsSI
import datetime
diagram = FluidPropertyDiagram('water')
diagram.set_unit_system(T='°C', p='bar', s='kJ/kgK', h='kJ/kg')

creation_date = datetime.datetime.now().strftime("%Y-%m-%d") 

iso_T = np.arange(50, 701, 50)
iso_h = np.arange(0, 4000, 100)
iso_v =[]
iso_v.extend([1e-3])
iso_v.extend(np.arange(0, 10, 2)/1000+0.002)
iso_v.extend(np.arange(0, 10, 2)/100+0.02)
iso_v.extend(np.arange(0, 10, 2)/10+0.2)
iso_v.extend(np.arange(0, 10, 2)+2)
iso_v.extend(np.arange(0, 10, 2)*10+20)
iso_v.extend(np.arange(0, 10, 2)*100+200)
iso_v = np.array(iso_v)
print([iso_v])
iso_p =[]
iso_p.extend([0.01])
iso_p.extend(np.arange(2, 10, 2)/100+0.02)
iso_p.extend(np.arange(0, 10, 2)/10+0.2)
iso_p.extend(np.arange(0, 10, 2)+2)
iso_p.extend(np.arange(0, 10, 2)*10+20)
iso_p.extend(np.arange(0, 10, 2)*100+200)
iso_p = np.array(iso_p)
print(iso_p)
iso_Q = np.linspace(0, 1, 11)
xmax = PropsSI('S', 'T', 273.15, 'Q', 1, 'Water') / 1e3

diagram.set_isolines(T=iso_T, h=iso_h, Q=iso_Q, p=iso_p, v=iso_v)
diagram.calc_isolines()
fig, ax = plt.subplots(1, figsize=(11.69, 8.27))

diagram.draw_isolines(diagram_type='Ts', 
    isoline_data={
        'h': { 'values': iso_h, 'style': {'linewidth': 1, 'color': 'green', 'linestyle': '-'}, }, # Solid line 
        'p': { 'values': iso_p, 'style': {'linewidth': 1, 'color': 'gray', 'linestyle': '-'}, }, # Solid line 
        'Q': { 'values': iso_Q, 'style': {'linewidth': 0.5, 'color': 'blue', 'linestyle': '-'}, }, # Solid line 
                      #'v': {'values': np.array([])} # Print no lines
    },
    fig=fig, ax=ax, x_min=0, x_max=xmax, y_min=0, y_max=700)
# Enable LaTeX formatting in Matplotlib
plt.rc('text', usetex=True)
plt.rc('font', family='serif')  # Optional: Set the font to be LaTeX's default serif font

ax.set_title(r'T-s Diagram for Water and Steam (IAPWS-IF97)', fontsize=14, fontweight='bold')
# Update the axis labels with LaTeX formatting
ax.set_xlabel(r'Entropy, $s$ (kJ/kg$\cdot$K)', fontsize=12)
ax.set_ylabel(r'Temperature, $T$ ($^\circ$C)', fontsize=12)
plt.tight_layout()
# Generate data for Q=0 and Q=1 using CoolProp
pressure_range = np.linspace(0.001, 22.064, 500)  # Pressure range in MPa (0.001 MPa to critical pressure)

# Saturation line for Q=0 (saturated liquid)
T_Q0 = []
s_Q0 = []
h_Q0 = []
for p in pressure_range:
    p_pa = p * 1e6  # Convert MPa to Pa
    T = PropsSI('T', 'P', p_pa, 'Q', 0, 'Water') - 273.15  # Saturation temperature in °C
    s = PropsSI('S', 'P', p_pa, 'Q', 0, 'Water') / 1e3  # Entropy in kJ/kgK
    h = PropsSI('H', 'P', p_pa, 'Q', 0, 'Water') / 1e3 # Enthalpy in J/kgK
    T_Q0.append(T)
    s_Q0.append(s)
    h_Q0.append(h)

# Saturation line for Q=1 (saturated vapor)
T_Q1 = []
s_Q1 = []
h_Q1 = []
for p in pressure_range:
    p_pa = p * 1e6  # Convert MPa to Pa
    T = PropsSI('T', 'P', p_pa, 'Q', 1, 'Water') - 273.15  # Saturation temperature in °C
    s = PropsSI('S', 'P', p_pa, 'Q', 1, 'Water') / 1e3  # Entropy in kJ/kgK
    h = PropsSI('H', 'P', p_pa, 'Q', 1, 'Water') / 1e3  # Enthalpy in kJ/kgK
    T_Q1.append(T)
    s_Q1.append(s)
    h_Q1.append(h)

# Plot the saturation lines for Q=0 and Q=1
ax.plot(s_Q0, T_Q0, label="Q=0 (Saturated Liquid)", linewidth=1.5, color='blue')
ax.plot(s_Q1, T_Q1, label="Q=1 (Saturated Vapor)", linewidth=1.5, color='blue')
ax.set_title(r'T-s Diagram for Water and Steam (IAPWS-IF97)', fontsize=14, fontweight='bold')
# Update the axis labels with LaTeX formatting
ax.set_xlabel(r'Entropy, $s$ (J/kg$\cdot$K)', fontsize=12)
ax.set_ylabel(r'Temperature, $T$ (°C)', fontsize=12)
ax.grid(visible=True, which='major', linestyle='-', linewidth=0.5, color='gray')  # Major gridlines
ax.grid(visible=True, which='minor', linestyle=':', linewidth=0.3, color='lightgray')  # Minor gridlines
ax.minorticks_on()

ax.text(
    0.02, 0.97,  # X and Y position in axes coordinates (0.95 = 95% from left, 0.02 = 2% from bottom)
    f"Created by Olof Björkqvist\nolof@bjorkqvist.nu\nCC BY-SA 4.0\nGenerated: {creation_date}",
    fontsize=10,
    color='gray',
    ha='left',  # Horizontal alignment: right-aligned
    va='top',  # Vertical alignment: bottom-aligned
    transform=ax.transAxes,  # Use axes coordinates for placement
    bbox=dict(facecolor='white', edgecolor='none', alpha=0.8)
)


# Save the h-s diagram
plt.tight_layout()
plt.show()
fig.savefig('Ts_Diagram.pdf')
fig.savefig('Ts_Diagram.svg', format='svg')
fig.savefig('Ts_Diagram.png', format='png', dpi=300)

fig, ax = plt.subplots(1, figsize=(297/25.4, 210/25.4))
diagram.draw_isolines(
    isoline_data={
        'T': { 'values': iso_T, 'style': {'linewidth': 0.5, 'color': 'red', 'linestyle': '-'}, }, # Solid line 
        'Q': { 'values': iso_Q, 'style': {'linewidth': 0.5, 'color': 'blue', 'linestyle': '-'}, }, # Solid line 
        'p': { 'values': iso_p, 'style': {'linewidth': 0.5, 'color': 'blue', 'linestyle': '-'}, }, # Solid line 
        'v': {'values': np.array([])} # Print no lines
    },
    diagram_type='hs', fig=fig, ax=ax, x_min=0, x_max=xmax, y_min=0, y_max=3600)
ax.plot(s_Q0, h_Q0, label="Q=0 (Saturated Liquid)", linewidth=1.5, color='blue')
ax.plot(s_Q1, h_Q1, label="Q=1 (Saturated Vapor)", linewidth=1.5, color='blue')
ax.set_title(r'h-s Diagram for Water and Steam (IAPWS-IF97)', fontsize=14, fontweight='bold')
# Update the axis labels with LaTeX formatting
ax.set_xlabel(r'Entropy, $s$ (kJ/kg$\cdot$K)', fontsize=12)
ax.set_ylabel(r'Enthalpy, $h$ (kJ/kg)', fontsize=12)
ax.grid(visible=True, which='major', linestyle='-', linewidth=0.5, color='gray')  # Major gridlines
ax.grid(visible=True, which='minor', linestyle=':', linewidth=0.3, color='lightgray')  # Minor gridlines
ax.minorticks_on()

ax.text(
    0.97, 0.02,  # X and Y position in axes coordinates (0.95 = 95% from left, 0.02 = 2% from bottom)
    f"Created by Olof Björkqvist\nolof@bjorkqvist.nu\nCC BY-SA 4.0\nGenerated: {creation_date}",
    fontsize=10,
    color='gray',
    ha='right',  # Horizontal alignment: right-aligned
    va='bottom',  # Vertical alignment: bottom-aligned
    transform=ax.transAxes,  # Use axes coordinates for placement
    bbox=dict(facecolor='white', edgecolor='none', alpha=0.8)
)

plt.tight_layout()
plt.show()

fig.savefig('hs_Diagram_full.pdf')
fig.savefig('hs_Diagram_full.svg', format='svg')
fig.savefig('hs_Diagram_full.png', format='png', dpi=300)

fig, ax = plt.subplots(1, figsize=(297/25.4, 210/25.4))
diagram.draw_isolines(
    isoline_data={
        'T': { 'values': iso_T, 'style': {'linewidth': 1, 'color': 'red', 'linestyle': '-'}, }, # Solid line 
        'Q': { 'values': iso_Q, 'style': {'linewidth': 0.5, 'color': 'blue', 'linestyle': '-'}, }, # Solid line 
        'p': { 'values': iso_p, 'style': {'linewidth': 0.5, 'color': 'blue', 'linestyle': '-'}, }, # Solid line 
        'v': { 'values': iso_v, 'style': {'linewidth': 0.5, 'color': 'black', 'linestyle': ':'}, }, # Solid line 
    },
    diagram_type='hs', fig=fig, ax=ax, x_min=5, x_max=9, y_min=1900, y_max=4000)
ax.plot(s_Q0, h_Q0, label="Q=0 (Saturated Liquid)", linewidth=1.5, color='blue')
ax.plot(s_Q1, h_Q1, label="Q=1 (Saturated Vapor)", linewidth=1.5, color='blue')
ax.set_title(r'h-s Diagram for Water and Steam (IAPWS-IF97)', fontsize=14, fontweight='bold')
# Update the axis labels with LaTeX formatting
ax.set_xlabel(r'Entropy, $s$ (kJ/kg$\cdot$K)', fontsize=12)
ax.set_ylabel(r'Enthalpy, $h$ (kJ/kg)', fontsize=12)

ax.grid(visible=True, which='major', linestyle='-', linewidth=0.5, color='gray')  # Major gridlines
ax.grid(visible=True, which='minor', linestyle=':', linewidth=0.3, color='lightgray')  # Minor gridlines
ax.minorticks_on()

ax.text(
    0.97, 0.02,  # X and Y position in axes coordinates (0.95 = 95% from left, 0.02 = 2% from bottom)
    f"Created by Olof Björkqvist\nolof@bjorkqvist.nu\nCC BY-SA 4.0\nGenerated: {creation_date}",
    fontsize=10,
    color='gray',
    ha='right',  # Horizontal alignment: right-aligned
    va='bottom',  # Vertical alignment: bottom-aligned
    transform=ax.transAxes,  # Use axes coordinates for placement
    bbox=dict(facecolor='white', edgecolor='none', alpha=0.8)
)

plt.tight_layout()
plt.show()
fig.savefig('hs_Diagram_part.pdf')
fig.savefig('hs_Diagram_part.svg', format='svg')
fig.savefig('hs_Diagram_part.png', format='png', dpi=300)
