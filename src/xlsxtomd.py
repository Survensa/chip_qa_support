import openpyxl

def xlsx_to_md(input_file, output_file):
    # Load the Excel workbook
    workbook = openpyxl.load_workbook(input_file)

    # Open the first sheet (you can modify this to select a specific sheet)
    sheet = workbook.active

    # Open the output file in write mode
    with open(output_file, 'w') as md_file:
        for i, row in enumerate(sheet.iter_rows(), start=1):
            # Iterate through the cells in the row
            md_row = "|".join(f"**{cell.value}**" if cell.value is not None and i == 1 else str(cell.value) if cell.value is not None else "" for cell in row)
            # Write the Markdown row to the output file
            md_file.write(md_row + "\n")

if __name__ == "__main__":
    input_file = "Docs/TC_Summary.xlsx"  # Replace with your input Excel file
    output_file = "Docs/TC_Summary.md"  # Replace with your desired output Markdown file name

    xlsx_to_md(input_file, output_file)
