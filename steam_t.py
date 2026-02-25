from iapws import IAPWS97
import subprocess
from jinja2 import Environment, FileSystemLoader
import os

# Constants for water properties
triple = IAPWS97(P=0.000611657, T=273.16)
print (triple.T)
crit = IAPWS97(P=22.064, T=647.096)

# Pressure ranges
#lowest_pressures = [round(p * 0.01, 2) for p in range(1, 10)]  # 0.1 to 0.9 bar in steps of 0.1 bar
#print("Lowest pressures:", lowest_pressures)  # Debug: Print lowest pressure list
#low_pressures = [round(p * 0.1, 1) for p in range(1, 10)]  # 0.1 to 0.9 bar in steps of 0.1 bar
#medium_pressures = range(1, 10)  # 1 to 9 bar
#high_pressures = range(10, 220, 10)  # 10, 20, ..., 100 bar

# Temperature parameters
start_temp = 5  # Stop temperature in °C
stop_temp = int(crit.T - 273.15)+1  # Stop temperature in °C

temperature = range(start_temp, stop_temp, 5)  # 10, 20, ..., 100 bar

def format_value(value, significant_figures=6, custom_figures=None):
    """
    Formats a float value to a specified number of significant figures.
    
    Parameters:
    - value: The value to format (float).
    - significant_figures: Default number of significant figures (default is 6).
    - custom_figures: Optional parameter to override the number of significant figures.
    
    Returns:
    - Formatted string with the desired number of significant figures.
    """
    if isinstance(value, float):
        # Use custom figures if provided, otherwise use the default significant_figures
        figures = custom_figures if custom_figures is not None else significant_figures

        # Count total digits and determine decimal places needed
        from math import floor, log10

        if value == 0:
            decimals = figures - 1
        else:
            decimals = max(figures - 1 - floor(log10(abs(value))), 0)

        # Format the value with the calculated number of decimals
        formatted = f"{value:.{decimals}f}"  # Fixed-point with required decimals
        formatted = formatted.replace('.', ',')  # Replace decimal point with comma
        return formatted
    return value  # Return as-is for non-float types

# Jinja2 setup
env = Environment(loader=FileSystemLoader("."))  # Load templates from current directory
template = env.get_template("steamtables_ttable.tex")

# Read the LaTeX preamble
with open("steamtables_preamble.tex", "r") as preamble_file:
    preamble_content = preamble_file.read()

# Prepare LaTeX content for all tables
all_tables_latex = ""


table_data = []

table_data.append([
    format_value(triple.T-273.15, 2),                    # Temperature in °C
    format_value(triple.P * 10),                        # Pressure in bar
    format_value(IAPWS97(T=triple.T, x=0).v),
    format_value(IAPWS97(T=triple.T, x=1).v),
    format_value(IAPWS97(T=triple.T, x=0).h, 4),
    format_value(IAPWS97(T=triple.T, x=1).h - IAPWS97(T=triple.T, x=0).h),
    format_value(IAPWS97(T=triple.T, x=1).h),
    format_value(abs(IAPWS97(T=triple.T, x=0).s*0), 1),
    format_value(IAPWS97(T=triple.T, x=1).s)
])

for temperature in temperature:
    
    # Saturated liquid (x=0)
    steam = IAPWS97(T=temperature+273.15, x=0)
    table_data.append([
        temperature,
        format_value(IAPWS97(T=temperature+273.15, x=0).P * 10),
        format_value(IAPWS97(T=temperature+273.15, x=0).v),
        format_value(IAPWS97(T=temperature+273.15, x=1).v),
        format_value(IAPWS97(T=temperature+273.15, x=0).h),
        format_value(IAPWS97(T=temperature+273.15, x=1).h - IAPWS97(T=temperature+273.15, x=0).h),
        format_value(IAPWS97(T=temperature+273.15, x=1).h),
        format_value(IAPWS97(T=temperature+273.15, x=0).s),
        format_value(IAPWS97(T=temperature+273.15, x=1).s)
    ])
    


table_data.append([
    format_value(crit.T - 273.15),                    # Temperature in °C
    format_value(crit.P * 10),                        # Pressure in bar
    format_value(crit.v),                             # Specific volume (same for liquid/gas at critical)
    format_value(crit.v),
    format_value(crit.h),
    "-",                                               # No latent heat at critical point
    format_value(crit.h),
    format_value(crit.s),
    format_value(crit.s),
])

# Render the table for all pressures
table_header_text = f"Saturated steam properties as a function of temperature"
rendered_table = template.render(
    table_header_text=table_header_text,
    table_data=table_data
)
    

# Append table to the combined LaTeX document
#all_tables_latex += rendered_table + "\n\\newpage\n"
all_tables_latex += rendered_table

# Combine the preamble and the tables into a final LaTeX document
final_latex_document = (
    preamble_content +
    "\\begin{document}\n" +
    all_tables_latex +
    "\\end{document}\n"
)

# Write the combined LaTeX content to a file
tex_filename = "steam_t.tex"
pdf_filename = "steam_t.pdf"

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
