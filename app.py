from flask import Flask, render_template, request, send_file
import qrcode
import io

app = Flask(__name__)

def generate_qr(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    qr_img = qr.make_image(fill='black', back_color='white')

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

        img_byte_arr = generate_qr(data)
        if img_byte_arr:
            return send_file(img_byte_arr, mimetype='image/png', as_attachment=True, download_name=f"{ssid}.png")
        else:
            return "Error generating QR code.", 400

    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
