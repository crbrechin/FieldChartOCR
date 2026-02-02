from homework_signer import insert_barcode_into_svg

# Change this to whatever message you want to encode
barcode_data = "HELLO123"  # <-- Change this to your desired message

# Generate the barcode
insert_barcode_into_svg("calibration_page-coloured.svg", barcode_data, "output.svg")
print(f"Barcode inserted successfully with message: {barcode_data}")

