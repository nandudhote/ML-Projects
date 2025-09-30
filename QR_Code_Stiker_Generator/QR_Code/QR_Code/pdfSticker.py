import qrcode
from reportlab.lib.pagesizes import portrait
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

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

    # Save the PDF
    c.save()

# Data for the sticker
data = {
    "Device Name:": "Smart LED Light",
    "Model No   :": "EZN-LED-2x2-60",
    "Serial No  :": "ledAABBDF",
    "MAC ID     :": "8C:4C:AD:F0:BD:E6",
    "MDF By     :": "EVOLUZN INDIA PRIVATE LIMITED",
}

# QR code data (Serial No)
qr_data = data["Serial No  :"]

# Output file path
output_file = "sticker.pdf"

# Generate sticker
generate_sticker(data, qr_data, output_file)

print("Sticker generated successfully.")
