
.PHONY: install uninstall check-deps test clean help

PYTHON = python3
PIP = pip3
SCRIPT = thermal.py
REQUIREMENTS = requirements.txt

install: check-deps install-system-deps install-python-deps fix-permissions
	@echo "Installation completed successfully!"

install-system-deps:
	@echo "Installing system dependencies..."
	sudo apt update
	sudo apt install -y imagemagick ghostscript texlive-extra-utils cups
	@echo "System dependencies installed!"

install-python-deps:
	@echo "Installing Python dependencies..."
	if command -v apt > /dev/null 2>&1; then \
		sudo apt install -y python3-pil python3-escpos || \
		($(PIP) install -r $(REQUIREMENTS) && echo "Python dependencies installed via pip!"); \
	else \
		$(PIP) install -r $(REQUIREMENTS) && echo "Python dependencies installed via pip!"; \
	fi

install-pip:
	@echo "Installing Python dependencies via pip..."
	$(PIP) install -r $(REQUIREMENTS)

# Check dependencies
check-deps:
	@echo "Checking dependencies..."
	@if ! command -v $(PYTHON) > /dev/null 2>&1; then \
		echo "Python3 not found. Please install Python 3."; \
		exit 1; \
	fi
	@echo "Dependency check passed!"

# Fix permissions
fix-permissions:
	@echo "Setting up permissions..."
	sudo usermod -a -G lp $$USER 2>/dev/null || true
	@if ! grep -q 'SUBSYSTEM=="usb"' /etc/udev/rules.d/99-thermal-printer.rules 2>/dev/null; then \
		echo 'SUBSYSTEM=="usb", MODE="0666", GROUP="lp"' | sudo tee /etc/udev/rules.d/99-thermal-printer.rules > /dev/null; \
		sudo udevadm control --reload-rules; \
		sudo udevadm trigger; \
		echo "udev rules updated!"; \
	fi
	@echo "Please reconnect printer or reboot for permission changes to take effect"

# Test installation
test:
	@echo "Testing installation..."
	@if $(PYTHON) $(SCRIPT) --help > /dev/null 2>&1; then \
		echo "Tool is working correctly!"; \
	else \
		echo "Tool test failed!"; \
		exit 1; \
	fi

# Uninstall
uninstall:
	@echo "Uninstalling dependencies..."
	sudo apt remove -y texlive-extra-utils 2>/dev/null || true
	$(PIP) uninstall -y -r $(REQUIREMENTS) 2>/dev/null || true
	@echo "Dependencies uninstalled!"

# Clean up
clean:
	@echo "Cleaning up..."
	rm -f *.bmp *.pdf_crop *.log 2>/dev/null || true
	@echo "Cleaned up!"

# Help
help:
	@echo "Thermal Printer Tool Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make install     - Install all dependencies"
	@echo "  make install-pip - Install only Python dependencies via pip"
	@echo "  make check-deps  - Check if all dependencies are available"
	@echo "  make test        - Test the installation"
	@echo "  make uninstall   - Uninstall dependencies"
	@echo "  make clean       - Clean temporary files"
	@echo "  make help        - Show this help"
