from flask import Flask, render_template, request, send_file
import qrcode
from PIL import Image
import os
import io

app = Flask(__name__)

def generate_qr_with_logo(data, logo_path, ssid):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,  # Increased box size for a larger QR code
        border=2,     # Reduced border thickness
    )
    qr.add_data(data)
    qr.make(fit=True)

    qr_img = qr.make_image(fill='black', back_color='white').convert('RGB')

    try:
        logo = Image.open(logo_path)
    except FileNotFoundError:
        return None

    qr_width, qr_height = qr_img.size
    larger_logo_size = (qr_width // 3) * 2 // 3  # Reduce the logo size to about 3/4ths
    logo = logo.resize((larger_logo_size, larger_logo_size), Image.Resampling.LANCZOS)

    white_box_size = (larger_logo_size + 14, larger_logo_size + 14)  # Adjust white box size accordingly
    white_box = Image.new("RGBA", white_box_size, "white")
    white_box.paste(logo, (7, 7), logo.convert("RGBA"))

    logo_position = ((qr_width - white_box_size[0]) // 2, (qr_height - white_box_size[1]) // 2)
    qr_img = qr_img.convert("RGBA")
    qr_img.paste(white_box, logo_position, white_box)

    img_byte_arr = io.BytesIO()
    qr_img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    return img_byte_arr

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        ssid = request.form['ssid']
        password = request.form['password']
        encryption = request.form['encryption']

        data = f"WIFI:T:{encryption};S:{ssid};P:{password};;"
        logo_path = os.path.join(app.root_path, 'logo.png')  # Ensure logo path is correct

        img_byte_arr = generate_qr_with_logo(data, logo_path, ssid)
        if img_byte_arr:
            return send_file(img_byte_arr, mimetype='image/png', as_attachment=True, download_name=f"{ssid}.png")
        else:
            return "Error generating QR code. Logo file not found.", 400

    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
