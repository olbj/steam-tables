from iapws import IAPWS97
import subprocess
from jinja2 import Environment, FileSystemLoader
import os

# Pressure ranges
lowest_pressures = [round(p * 0.01, 2) for p in range(1, 10)]  # 0.1 to 0.9 bar in steps of 0.1 bar
print("Lowest pressures:", lowest_pressures)  # Debug: Print lowest pressure list
low_pressures = [round(p * 0.1, 1) for p in range(1, 10)]  # 0.1 to 0.9 bar in steps of 0.1 bar
medium_pressures = range(1, 10)  # 1 to 9 bar
high_pressures = range(10, 101, 10)  # 10, 20, ..., 100 bar
higher_pressures = range(125, 351, 25)  # 10, 20, ..., 100 bar

# Temperature parameters
temperature_step = 10  # Step size in °C
num_temperatures = 57  # Number of temperatures besides the saturation temperatures

def format_value(value, significant_figures=8):
    if isinstance(value, float):
        # Count total digits and determine decimal places needed
        from math import floor, log10

        if value == 0:
            decimals = significant_figures - 1
        else:
            decimals = max(significant_figures - 1 - floor(log10(abs(value))), 0)

        formatted = f"{value:.{decimals}f}"  # fixed-point with required decimals
        formatted = formatted.replace('.', ',')  # replace decimal point with comma
        return formatted
    return value  # Return as-is for non-float types
# Helper function to format values to 8 significant figures

#-def format_value(value, significant_figures=8):
#    if isinstance(value, float):
#        # Use scientific notation for precise significant figures
#        return f"{value:.{significant_figures}g}"
#    return value  # Return the value as-is for non-float types

# Jinja2 setup
env = Environment(loader=FileSystemLoader("."))  # Load templates from current directory
template = env.get_template("steamtables_table.tex")

# Read the LaTeX preamble
with open("steamtables_preamble.tex", "r") as preamble_file:
    preamble_content = preamble_file.read()

# Prepare LaTeX content for all tables
all_tables_latex = ""

# Generate steam tables for each pressure
pressures = lowest_pressures + low_pressures + list(medium_pressures) + list(high_pressures) + list(higher_pressures)
print("Pressures:", pressures)  # Debug: Print pressure list

for pressure in pressures:

    table_data = []
    if pressure * 0.1 < 22.064:
        # Calculate saturation temperature
        saturation_temp = IAPWS97(P=pressure * 0.1, x=1).T - 273.15  # Convert P to MPa and T from K to °C

        # Generate temperature range: exactly 57 temperatures beyond the saturation temperature
        start_temperature = int((saturation_temp) / 10 + 1) * 10  # Start at the next 10°C above the saturation temperature
        temperatures = [start_temperature + i * temperature_step for i in range(num_temperatures)]

        # Calculate steam properties for saturated and overheated states
    
        # Saturated liquid (x=0)
        steam = IAPWS97(P=pressure * 0.1, x=0)
        table_data.append([
            format_value(steam.T - 273.15),
            format_value(steam.v),
            format_value(steam.h),
            format_value(steam.s),
            steam.x
        ])
    
        # Saturated vapor (x=1)
        steam = IAPWS97(P=pressure * 0.1, x=1)
        table_data.append([
            format_value(steam.T - 273.15),
            format_value(steam.v),
            format_value(steam.h),
            format_value(steam.s),
            steam.x
        ])
    else: 

        # Generate temperature range: exactly 57 temperatures beyond the saturation temperature
        tcrit = 647.096 - 273.15  # Critical temperature in °C
        start_temperature = int((tcrit) / 10 + 1) * 10  # Start at the next 10°C above the saturation temperature
        temperatures =  [False] +  [tcrit] + [start_temperature + i * temperature_step for i in range(num_temperatures)]
        print(tcrit, start_temperature)  # Debug: Print critical temperature and start temperature
        print(start_temperature, temperatures)  # Debug: Print temperature 

    # Overheated steam
    for T in temperatures:
        if T is False:
            table_data.append(["Critical t", "", ""])  # Placeholder for the critical point
        else:
            steam = IAPWS97(P=pressure * 0.1, T=T + 273.15)  # Overheated steam
            table_data.append([ T, format_value(steam.v), format_value(steam.h), format_value(steam.s), steam.x ])

    # Render the table for this pressure
    table_header_text = f"Steam properties. Single phase region. {str(pressure).replace('.', ',')} bar."
    rendered_table = template.render(
        table_header_text=table_header_text,
        table_data=table_data,
    )
    
    print(rendered_table[:500])  # Debug: Print the first 500 characters of the LaTeX table

    # Append table to the combined LaTeX document
    all_tables_latex += rendered_table + "\n\\newpage\n"

# Combine the preamble and the tables into a final LaTeX document
final_latex_document = (
    preamble_content +
    "\\begin{document}\n" +
    all_tables_latex +
    "\\end{document}\n"
)

# Write the combined LaTeX content to a file
tex_filename = "steam.tex"
pdf_filename = "steam.pdf"

with open(tex_filename, "w") as f:
    f.write(final_latex_document)

# Compile the LaTeX document into a PDF
try:
    subprocess.run(["pdflatex", "-interaction=nonstopmode", tex_filename], check=True)
    print(f"✅ PDF generated: {pdf_filename}")
except subprocess.CalledProcessError as e:
    print("❌ Error during LaTeX compilation")
    print(e)

# Clean up auxiliary files
for ext in [".aux", ".log", ".out"]:
    aux_file = tex_filename.replace(".tex", ext)
    if os.path.exists(aux_file):
        os.remove(aux_file)
