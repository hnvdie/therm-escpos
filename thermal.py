#!/usr/bin/env python3
import sys
import os
import argparse
import subprocess
import tempfile
from escpos.printer import Usb
from PIL import Image
import textwrap

# Global variables
VENDOR_ID = 0x20d1
PRODUCT_ID = 0x7008

def crop_pdf(pdf_file):
    """Crop PDF to remove margins"""
    try:
        # Create a temporary file for the cropped PDF
        base_name = os.path.splitext(pdf_file)[0]
        cropped_file = f"{base_name}_cropped.pdf"
        
        command = ["pdfcrop", pdf_file, cropped_file]
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"Warning: pdfcrop failed: {result.stderr}")
            return pdf_file  # Return original if cropping fails
        
        return cropped_file
    except Exception as e:
        print(f"Warning: PDF cropping error: {e}")
        return pdf_file  # Return original if cropping fails

def convert_pdf_to_image(pdf_file, output_file="out.bmp"):
    """Convert PDF to a high-contrast bitmap suitable for thermal printing"""
    try:
        cmd = [
            "convert",
            "-density", "300",  # Higher density for better quality
            "-colorspace", "gray",
            "-normalize",
            "-threshold", "60%",  # Better threshold for thermal printing
            "-trim",  # Remove any white borders
            "+repage",  # Remove canvas metadata
            pdf_file,
            output_file
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting PDF: {e}")
        return False
    except FileNotFoundError:
        print("Error: ImageMagick not installed. Install with: sudo apt install imagemagick")
        return False

def convert_txt_to_image(txt_file, output_file="out.bmp"):
    """Convert text file to an image for thermal printing"""
    try:
        # Read text file
        with open(txt_file, 'r', encoding='utf-8', errors='ignore') as f:
            text_content = f.read()
        
        # Wrap text to appropriate width for thermal printer (typically 32-48 characters)
        wrapped_text = textwrap.fill(text_content, width=42)
        
        # Create a temporary image with the text
        from PIL import Image, ImageDraw, ImageFont
        
        # Try to use a monospaced font
        try:
            font = ImageFont.truetype("DejaVuSansMono.ttf", 12)
        except:
            try:
                font = ImageFont.truetype("LiberationMono-Regular.ttf", 12)
            except:
                font = ImageFont.load_default()
        
        # Calculate image size based on text
        lines = wrapped_text.split('\n')
        line_height = 14
        img_width = 576  # Typical thermal printer width in pixels
        img_height = len(lines) * line_height + 20
        
        # Create image
        img = Image.new('1', (img_width, img_height), 1)  # 1 for white background
        draw = ImageDraw.Draw(img)
        
        # Draw text
        y = 10
        for line in lines:
            draw.text((10, y), line, font=font, fill=0)  # 0 for black text
            y += line_height
        
        # Save as BMP
        img.save(output_file)
        return True
    except Exception as e:
        print(f"Error converting text to image: {e}")
        return False

def print_image(image_file):
    """Print image to thermal printer"""
    try:
        p = Usb(VENDOR_ID, PRODUCT_ID, interface=0, in_ep=0x81, out_ep=0x02)
        image = Image.open(image_file)
        
        # Check if we need to resize for thermal printer width (typically 576 pixels)
        if image.width > 576:
            ratio = 576 / image.width
            new_height = int(image.height * ratio)
            image = image.resize((576, new_height), Image.LANCZOS)
        
        p.image(image, center=True)
        p.cut()
        return True
    except Exception as e:
        print(f"Error printing: {e}")
        return False

def main():
    global VENDOR_ID, PRODUCT_ID
    
    parser = argparse.ArgumentParser(description="Thermal printer POS tool")
    parser.add_argument("--file", help="File to print (PDF, TXT, BMP, PNG, JPG)")
    parser.add_argument("--vendor", help="Vendor ID of your printer (hex format)", default="0x20d1")
    parser.add_argument("--product", help="Product ID of your printer (hex format)", default="0x7008")
    parser.add_argument("--no-crop", action="store_true", help="Disable PDF cropping")
    args = parser.parse_args()

    # Parse vendor and product IDs
    try:
        VENDOR_ID = int(args.vendor, 16)
        PRODUCT_ID = int(args.product, 16)
    except ValueError:
        print("Error: Vendor and Product IDs must be in hex format (e.g., 0x20d1)")
        sys.exit(1)

    if not args.file:
        parser.print_help()
        sys.exit(1)

    pdf_file = args.file
    if not os.path.isfile(pdf_file):
        print(f"Error: File not found: {pdf_file}")
        sys.exit(1)

    # Create a temporary directory for intermediate files
    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = os.path.join(temp_dir, "out.bmp")
        file_extension = os.path.splitext(pdf_file)[1].lower()
        
        try:
            if file_extension == '.pdf':
                print("[*] Processing PDF file...")
                
                if not args.no_crop:
                    print("[*] Cropping PDF...")
                    pdf_file = crop_pdf(pdf_file)
                
                print("[*] Converting PDF to image...")
                if not convert_pdf_to_image(pdf_file, output_file):
                    sys.exit(1)
                    
            elif file_extension == '.txt':
                print("[*] Processing text file...")
                if not convert_txt_to_image(pdf_file, output_file):
                    sys.exit(1)
                    
            elif file_extension in ['.bmp', '.png', '.jpg', '.jpeg']:
                print("[*] Processing image file...")
                # For image files, just use them directly
                output_file = pdf_file
            else:
                print(f"Error: Unsupported file format: {file_extension}")
                sys.exit(1)
            
            print("[*] Printing to thermal printer...")
            if print_image(output_file):
                print("[✓] Print job completed successfully.")
            else:
                print("[✗] Print job failed.")
                sys.exit(1)
                
        except KeyboardInterrupt:
            print("\n[!] Print job cancelled by user.")
            sys.exit(1)
        except Exception as e:
            print(f"[✗] Unexpected error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
