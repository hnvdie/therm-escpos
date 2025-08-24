# therm-escpos
Tool untuk mencetak berbagai format file (PDF, TXT, gambar) ke printer thermal ESC/POS di Linux.

## Fitur

- Support multiple format: PDF, TXT, BMP, PNG, JPG
- Auto-cropping PDF (dapat dinonaktifkan)
- Konversi teks ke image dengan wrapping otomatis
- Error handling yang baik
- Support berbagai Vendor/Product ID printer

## Requirements

- Linux (tested on Linux Mint)
- Python 3.x
- Printer thermal ESC/POS compatible
  (tested on HPRT TP806)

## Dependencies

### System Dependencies
- ImageMagick (untuk konversi PDF ke image)
- Ghostscript (untuk processing PDF)
- pdfcrop (untuk cropping PDF)

### Python Dependencies
- python3-pil (Pillow untuk image processing)
- python3-escpos (driver untuk printer ESC/POS)

## Installation

### Makefile (Recommended)
```bash
git clone https://github.com/hnvdie/therm-escpos
cd therm-escpos
make install
```

### Usage:
```bash
python3 thermal.py --file struct.pdf --vendor 0x1234 --product 0x5678
```

### Contoh Vendor/Product ID
- Generic: `--vendor 0x20d1 --product 0x7008`
- Epson: `--vendor 0x04b8 --product 0x0e15`
- Star: `--vendor 0x0519 --product 0x0003`

## Menemukan Vendor/Product ID Printer

1. Hubungkan printer via USB
2. Jalankan perintah:
```bash
lsusb
```
3. Cari entry printer Anda, contoh:
```
Bus 001 Device 005: ID 20d1:7008  
```
Dimana `20d1` adalah Vendor ID dan `7008` adalah Product ID

### 1. Permission denied untuk USB device
```bash
# Tambahkan user ke grup lp
sudo usermod -a -G lp $USER

# atau buat rule udev
echo 'SUBSYSTEM=="usb", MODE="0666", GROUP="lp"' | sudo tee /etc/udev/rules.d/99-thermal-printer.rules
sudo udevadm control --reload-rules
```

## Contributing
1. Fork repository
2. Buat feature branch
3. Commit changes
4. Push ke branch
5. Buat Pull Request

