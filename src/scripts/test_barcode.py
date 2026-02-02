from homework_signer import insert_barcode_into_svg

# Test the barcode insertion
test_data = "HELLO123"
input_file = "calibration_page-coloured.svg"
output_file = "calibration_page-coloured_with_barcode.svg"

try:
    insert_barcode_into_svg(input_file, test_data, output_file)
    print(f"Successfully inserted barcode '{test_data}' into {input_file}")
    print(f"Output saved to {output_file}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

