# Streamlit Barcode Generator & Printer

A professional Streamlit web application for generating and printing Code128 barcodes with comprehensive print history tracking and management features.

To run:
```
streamlit run https://raw.githubusercontent.com/dannyphamv/streamlit-BarcodeApp/refs/heads/main/BarcodeApp.py
```
## 🚀 Features

- **Barcode Generation**: Generate Code128 barcodes from text input
- **Auto-Print**: Automatically prints barcodes when Enter is pressed
- **Printer Selection**: Choose from available system printers
- **Print History**: Complete tracking of all printed barcodes with timestamps
- **Reprint Functionality**: Select and reprint multiple barcodes from history
- **Cross-Platform Support**: Works on Windows (with full printing support) and other platforms
- **Persistent Configuration**: Remembers your last selected printer
- **Clean UI**: Modern, intuitive Streamlit interface

## 📋 Requirements

- Python 3.7+
- Windows (for full printing functionality)
- Available system printer

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/dannyphamv/streamlit-BarcodeApp.git
   cd streamlit-BarcodeApp
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run BarcodeApp.py
   ```

## 📦 Dependencies

- `streamlit>=1.28.0` - Web application framework
- `pandas>=1.5.0` - Data manipulation and analysis
- `python-barcode[images]>=0.15.1` - Barcode generation
- `Pillow==9.5.0` - Image processing
- `pywin32>=306` - Windows API access for printing

## 💻 Usage

### Basic Operation
1. Launch the application using `streamlit run BarcodeApp.py`
2. Select your desired printer from the dropdown
3. Enter or scan a barcode in the text input field
4. Press Enter to automatically generate and print the barcode

### Print History Management
- View all printed barcodes in the sidebar with timestamps
- Select multiple entries from the history table
- Use "Reprint Selected" to print multiple barcodes at once
- Clear entire print history with the "Clear Print History" button

### Configuration
- The app automatically saves your last selected printer
- Configuration and print history are stored in:
  - **Windows**: `%APPDATA%/BarcodeApp/`
  - **Other OS**: `~/.config/BarcodeApp/`

## 🏗️ Project Structure

```
streamlit-BarcodeApp/
├── BarcodeApp.py          # Main application file
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
└── LICENSE               # License file
```

## 🔧 Technical Details

### Barcode Generation
- Uses Code128 barcode format for maximum compatibility
- Generates 600x300 pixel labels with centered barcodes
- White background for professional appearance

### Printing (Windows Only)
- Direct GDI printing using Windows API
- Automatic scaling to fit printer's printable area
- Centered positioning on page

### Data Storage
- Print history stored in CSV format
- Configuration saved as JSON
- Automatic directory creation in user's app data folder

## 🐛 Troubleshooting

### Common Issues

1. **"Required barcode libraries are not installed"**
   ```bash
   pip install python-barcode[images]
   ```

2. **"Printing is only supported on Windows"**
   - Full printing functionality requires Windows
   - On other platforms, barcodes can still be generated and viewed

3. **"win32print module not installed"**
   ```bash
   pip install pywin32
   ```

### Platform Limitations
- **Windows**: Full functionality including printing
- **macOS/Linux**: Barcode generation and viewing only (printing not supported)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

If you encounter any issues or have questions, please [open an issue](https://github.com/dannyphamv/streamlit-BarcodeApp/issues) on GitHub.

## 🔄 Version History

- **v1.0.0** - Initial release with core barcode generation and printing functionality

