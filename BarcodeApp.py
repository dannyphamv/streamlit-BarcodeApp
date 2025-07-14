import csv
from datetime import datetime
import os
import sys
import subprocess
from pathlib import Path
import json

# --- Streamlit and data processing imports ---
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

# --- Optional barcode imports ---
try:
    import barcode as barcode_module
    from barcode.writer import ImageWriter

    barcode_available = True
except ImportError:
    barcode_module = None
    ImageWriter = None
    barcode_available = False

# --- Constants ---
# Create app data directory
APP_NAME = "BarcodeApp"
if sys.platform == "win32":
    APP_DATA_DIR = Path(os.environ.get("APPDATA", "")) / APP_NAME
else:
    APP_DATA_DIR = Path.home() / ".config" / APP_NAME

APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

CSV_FILE = APP_DATA_DIR / "print_history.csv"
CONFIG_FILE = APP_DATA_DIR / "config.json"


# --- Function definitions ---
def load_config():
    """Load configuration from JSON file"""
    default_config = {"last_printer": None, "auto_print_enabled": True}
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as config_file:
                loaded_config = json.load(config_file)
                # Merge with defaults in case new settings are added
                return {**default_config, **loaded_config}
        return default_config
    except (json.JSONDecodeError, OSError):
        return default_config


def save_config(config_data):
    """Save configuration to JSON file"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as config_file:
            json.dump(config_data, config_file, indent=2, ensure_ascii=False)
    except (OSError, TypeError):
        pass  # Silently fail if we can't save config


def get_printer_names():
    """
    Returns a list of printer names available on the OS.
    Works on Windows using win32print.
    """
    if sys.platform == "win32":
        try:
            import win32print

            printers = win32print.EnumPrinters(
                win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
            )
            return [printer[2] for printer in printers]
        except ImportError:
            return ["win32print module not installed"]
    else:
        # For non-Windows, try using lpstat if available
        try:
            output = subprocess.check_output(["lpstat", "-e"], universal_newlines=True)
            return [line.strip() for line in output.splitlines() if line.strip()]
        except Exception:
            return ["Printer listing not supported on this OS"]


def generate_barcode(barcode_data):
    """
    Generates a barcode image from the given data and returns the PIL Image object.
    Returns the Image object if successful, else None.
    """
    if not barcode_available or barcode_module is None or ImageWriter is None:
        st.error(
            "Required barcode libraries are not installed. Please install: pip install python-barcode[images]"
        )
        return None
    try:
        from PIL import Image
        import io

        # Use Code128 for general barcode support
        CODE128 = barcode_module.get_barcode_class("code128")
        code = CODE128(barcode_data, writer=ImageWriter())
        with io.BytesIO() as buffer:
            code.write(buffer)
            buffer.seek(0)
            barcode_img = Image.open(buffer)
            # Create a white label and center the barcode on it
            label_width, label_height = 600, 300
            label_img = Image.new("RGB", (label_width, label_height), 0xFFFFFF)
            barcode_x = (label_width - barcode_img.width) // 2
            barcode_y = (label_height - barcode_img.height) // 2
            label_img.paste(barcode_img, (barcode_x, barcode_y))
            return label_img
    except Exception as e:
        st.error(f"Barcode generation failed: {e}")
        return None


def print_barcode_image(image_obj, printer_name):
    """
    Sends the barcode image to the specified printer (Windows only) using direct GDI printing with Pillow and ImageWin.
    """
    if sys.platform != "win32":
        st.error("Printing is only supported on Windows.")
        return
    try:
        import win32ui
        from PIL import ImageWin
        import win32con

        # Use the provided image object
        img = image_obj
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(printer_name)
        printable_area = hDC.GetDeviceCaps(win32con.HORZRES), hDC.GetDeviceCaps(
            win32con.VERTRES
        )
        img_width, img_height = img.size
        scale = min(printable_area[0] / img_width, printable_area[1] / img_height)
        scaled_width = int(img_width * scale)
        scaled_height = int(img_height * scale)
        img = img.resize((scaled_width, scaled_height))
        hDC.StartDoc("Barcode Print")
        hDC.StartPage()
        dib = ImageWin.Dib(img)
        x = int((printable_area[0] - scaled_width) / 2)
        y = int((printable_area[1] - scaled_height) / 2)
        dib.draw(hDC.GetHandleOutput(), (x, y, x + scaled_width, y + scaled_height))
        hDC.EndPage()
        hDC.EndDoc()
        hDC.DeleteDC()
        st.success(f"Sent barcode to printer: {printer_name}")

        # Log print history
        log_print_history()
    except Exception as e:
        st.error(f"Printing failed: {e}")


# --- Print history logging ---
def log_print_history():
    """
    Appends a print record to print_history.csv with columns: barcode, date time printed
    """
    global input_barcode
    barcode_value = input_barcode if "input_barcode" in globals() else ""
    now = datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")
    write_header = False
    try:
        with open(CSV_FILE, "r", newline="", encoding="utf-8") as history_file:
            pass
    except FileNotFoundError:
        write_header = True
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as history_file:
        csv_writer = csv.writer(history_file)
        if write_header:
            csv_writer.writerow(["barcode", "date time printed"])
        csv_writer.writerow([barcode_value, now])


# --- Streamlit UI and logic ---
st.title("Barcode Printer")

# Load configuration
config = load_config()

# Get available printers
available_printers = get_printer_names()

# Set default printer selection
default_printer_index = 0
if config["last_printer"] and config["last_printer"] in available_printers:
    default_printer_index = available_printers.index(config["last_printer"])

select_printer = st.selectbox(
    "Select a printer:", available_printers, index=default_printer_index
)

# Save selected printer to config when it changes
if select_printer != config["last_printer"]:
    config["last_printer"] = select_printer
    save_config(config)

# Initialize session state for tracking input changes
if "previous_barcode" not in st.session_state:
    st.session_state.previous_barcode = ""

input_barcode = st.text_input(
    "Scan or type barcode, then hit Enter:",
    key="barcode_input",
    placeholder="ex. DT6qbz2RRMA",
)

# Auto-focus using HTML/JavaScript injection
components.html(
    """
<script>
    function focusInput() {
        // Try multiple selectors to find the input
        let input = parent.document.querySelector('input[data-testid="stTextInput"] input') ||
                   parent.document.querySelector('input[aria-label*="Scan or type barcode"]') ||
                   parent.document.querySelector('input[placeholder*="DT6qbz2RRMA"]') ||
                   parent.document.querySelector('.stTextInput input');
        
        if (input) {
            input.focus();
            input.click();
        }
    }
    
    // Focus immediately
    focusInput();
    
    // Focus on any click in the parent document
    parent.document.addEventListener('click', function(e) {
        // Small delay to ensure Streamlit has processed the click
        setTimeout(focusInput, 50);
    });
    
    // Retry focusing periodically for the first few seconds
    let retryCount = 0;
    const retryInterval = setInterval(function() {
        focusInput();
        retryCount++;
        if (retryCount > 10) {
            clearInterval(retryInterval);
        }
    }, 200);
</script>
""",
    height=0,
)

col1, col2, col3 = st.columns(3)

# Check if Enter was pressed (input changed and is not empty)
auto_print = False
if (
    input_barcode
    and input_barcode != st.session_state.previous_barcode
    and input_barcode.strip()
):
    auto_print = True
    st.session_state.previous_barcode = input_barcode

# Generate and display barcode image if input is provided
barcode_image = None
if input_barcode:
    barcode_image = generate_barcode(input_barcode)
    if barcode_image:
        # with col2:
        st.image(barcode_image, caption="Generated Barcode", use_container_width=True)

# Auto-print when Enter is pressed
if auto_print:
    if input_barcode and input_barcode.strip():
        # Regenerate barcode to ensure latest input is printed
        barcode_image = generate_barcode(input_barcode)
        if barcode_image:
            print_barcode_image(barcode_image, select_printer)
    else:
        st.warning("Please enter a barcode before printing.")


# Button to clear print history CSV
if col2.button("Clear Print History", type="secondary", use_container_width=True):
    with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["barcode", "date time printed"])
    st.success("Print history cleared.")

# Ensure print_history.csv exists with header before reading
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["barcode", "date time printed"])

df = pd.read_csv(CSV_FILE)
df = df.sort_values(by="date time printed", ascending=False)

st.sidebar.header("Print History")

# Add selection capability to the dataframe
if not df.empty:
    selected_rows = st.sidebar.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row",
    )

    # Show reprint button if rows are selected
    selected_rows_list = []
    if "selection" in selected_rows and "rows" in selected_rows["selection"]:
        selected_indices = selected_rows["selection"]["rows"]
        if selected_indices:
            selected_barcodes = df.iloc[selected_indices]["barcode"].tolist()
            selected_rows_list = selected_barcodes

    if selected_rows_list:
        st.sidebar.write(f"Selected {len(selected_rows_list)} item(s) for reprinting:")
        for barcode in selected_rows_list:
            st.sidebar.write(f"• {barcode}")

        if st.sidebar.button(
            "Reprint Selected", type="primary", use_container_width=True
        ):
            for barcode in selected_rows_list:
                if barcode and barcode.strip():  # Skip empty barcodes
                    reprint_image = generate_barcode(barcode)
                    if reprint_image:
                        print_barcode_image(reprint_image, select_printer)
            st.sidebar.success(
                f"Reprinted {len([b for b in selected_rows_list if b and b.strip()])} barcode(s)"
            )
else:
    st.sidebar.dataframe(df, use_container_width=True, hide_index=True)
    st.sidebar.write("No print history available.")

st.divider()
st.write("Hosted on [GitHub](https://github.com/dannyphamv/streamlit-BarcodeApp).")
