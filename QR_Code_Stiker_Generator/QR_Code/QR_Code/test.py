import qrcode
from PIL import Image

def generate_qr_code(link, file_name, scale_factor=10):
    # Create a QR code instance
    qr = qrcode.QRCode(
        version=1,  # Controls the size of the QR Code (1 is smallest)
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
        box_size=10,  # Size of each box (default is 10)
        border=4,  # Border thickness
    )

    # Add data to the QR code
    qr.add_data(link)
    qr.make(fit=True)

    # Create the image from the QR code instance
    img = qr.make_image(fill="black", back_color="white")

    # Scale the image to a higher resolution using the Pillow library
    size = (img.size[0] * scale_factor, img.size[1] * scale_factor)
    img = img.resize(size, Image.NEAREST)

    # Save the image in high resolution
    img.save(f"{file_name}.png")

# Example usage
link = "https://example.com"
file_name = "high_res_qr_code"
generate_qr_code(link, file_name)
