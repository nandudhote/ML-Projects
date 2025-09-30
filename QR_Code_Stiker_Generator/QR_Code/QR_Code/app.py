import csv
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import win32print
import win32api

class QRPrinter:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.qr_data = self.read_csv()
        self.project_folder = os.path.dirname(os.path.abspath(__file__))  # Get the path of the current working directory


    def read_csv(self):
        qr_data = []
        with open(self.csv_file, 'r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                qr_data.append(row)
        return qr_data

    def generate_qr_codes(self):
        qr_codes = []
        for row in self.qr_data:
            data = row[0]
            qr = qrcode.make(data, border=4)  # Add border to the QR code
            qr_codes.append((qr, row[0]))  # Append tuple of QR code and caption
        return qr_codes

    def print_qr_codes(self):
        temp_pdf = os.path.join(self.project_folder, "output.pdf")  # Specify the path for the PDF file
        print("temp_pdf",temp_pdf)
        pdf_canvas = canvas.Canvas(temp_pdf, pagesize=A4)

        x_margin = 50
        y_margin = 50
        qr_size = 100
        x_spacing = 20  # Reduced spacing between QR codes
        y_spacing = 20  # Reduced spacing between QR codes and captions

        # Calculate maximum number of QR codes per row dynamically
        max_per_row = int((A4[0] - 2 * x_margin) / (qr_size + x_spacing))

        # Calculate maximum number of QR codes per page dynamically
        max_per_page = int((A4[1] - 2 * y_margin) / (qr_size + y_spacing)) * max_per_row

        current_row = 0 
        current_column = 0
        total_qr_count = 0
        qr_codes = self.generate_qr_codes()

        for qr, caption in qr_codes:
            if total_qr_count % max_per_page == 0 and total_qr_count != 0:
                pdf_canvas.showPage()
                current_row = 0
                current_column = 0

            x = x_margin + current_column * (qr_size + x_spacing)
            y = A4[1] - y_margin - (current_row * (qr_size + y_spacing)) - qr_size

            pdf_canvas.rect(x, y, qr_size, qr_size)  # Draw border around the QR code
            pdf_canvas.drawInlineImage(qr, x + 4, y + 4, width=qr_size - 8, height=qr_size - 8)

            # Add caption inside the QR code border at the top
            caption_x = x + qr_size / 2
            caption_y = y + qr_size - 10  # Adjust the distance between the QR code and the caption
            pdf_canvas.setFont("Helvetica", 10)
            pdf_canvas.drawCentredString(caption_x, caption_y, caption)

            current_column += 1
            total_qr_count += 1

            if current_column >= max_per_row:
                current_row += 1
                current_column = 0

        pdf_canvas.save()

        # Get the default printer
        printer_name = win32print.GetDefaultPrinter()
        print("printer_name--",printer_name)

        # Open the PDF file for printing
        hprinter = win32print.OpenPrinter(printer_name)
        try:
            hjob = win32print.StartDocPrinter(hprinter, 1, (temp_pdf, None, "RAW"))
            try:
                win32print.StartPagePrinter(hprinter)
                win32print.WritePrinter(hprinter, open(temp_pdf, 'rb').read())
                win32print.EndPagePrinter(hprinter)
            finally:
                win32print.EndDocPrinter(hprinter)
        finally:
            win32print.ClosePrinter(hprinter)

        print("QR codes printed directly")

# Usage
printer = QRPrinter("demo.csv")
printer.print_qr_codes()
