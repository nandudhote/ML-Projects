import qrcode
from reportlab.lib.pagesizes import portrait
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import pandas as pd

def generate_serial_no(mac_id):
    # Remove colons from MAC ID and generate the Serial No
    return "tube" + mac_id.replace(":", "")[-6:]

def generate_sticker(data, qr_data, output_file):
    # Define sticker dimensions
    sticker_width = 50  # in mm
    sticker_height = 25  # in mm

    # Create a canvas for the PDF
    c = canvas.Canvas(output_file, pagesize=(sticker_width * mm, sticker_height * mm))

    # Define font
    font_size = 5
    font_name = "Helvetica-Bold"

    # Define data positions
    data_positions = {
        "Device Name:": (1 * mm, 21 * mm),
        "Model No   :": (1 * mm, 16 * mm),
        "Serial No  :": (1 * mm, 11 * mm),
        "MAC ID     :": (1 * mm, 6 * mm),
        "MDF By     :": (1 * mm, 2 * mm),  # Adjusted position for text
    }

    # Generate and draw QR code for Serial No
    qr = qrcode.make(qr_data)
    qr_file = "qr_code.png"
    qr.save(qr_file)
    c.drawImage(qr_file, (27 * mm), (1 * mm), width=25 * mm, height=25 * mm)

    # Delete the QR code file
    import os
    os.remove(qr_file)

    # Draw data
    for key, value in data.items():
        c.setFont(font_name, font_size)
        c.drawString(data_positions[key][0], data_positions[key][1], f"{key} {value}")

    # Save the canvas
    c.save()

def generate_stickers_from_excel(input_file, output_file):
    # Read MAC IDs from Excel
    excel_data = pd.read_excel(input_file)

    # Generate stickers for each MAC ID
    for index, row in excel_data.iterrows():
        data = {
            "Device Name:": "Smart Tube Light",
            "Model No   :": "EZN-LED-4F-48",
            "Serial No  :": generate_serial_no(row['MAC']),
            "MAC ID     :": row['MAC'],
            "MDF By     :": "EVOLUZN INDIA PRIVATE LIMITED",
        }
        qr_data = data["Serial No  :"]
        output_file_per_sticker = f"sticker_{index}.pdf"  # Unique output file for each sticker
        generate_sticker(data, qr_data, output_file_per_sticker)

    # Merge all sticker PDFs into one
    merge_pdf_files([f"sticker_{index}.pdf" for index in range(len(excel_data))], output_file)

def merge_pdf_files(input_files, output_file):
    from PyPDF2 import PdfWriter, PdfReader

    writer = PdfWriter()
    for file in input_files:
        reader = PdfReader(file)
        writer.add_page(reader.pages[0])  # Only add the first page (sticker) to the merged PDF

    with open(output_file, 'wb') as f:
        writer.write(f)

# Input and output file paths
input_file = "smartLED_MAC.xlsx"
output_file = "stickers.pdf"

# Generate stickers from Excel and save as PDF
generate_stickers_from_excel(input_file, output_file)

print("Stickers generated successfully.")
