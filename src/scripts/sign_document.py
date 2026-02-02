from homework_signer import sign_with_next_uuid

# Sign a document with the next available UUID
# You can customize the output filename
result = sign_with_next_uuid(
    csv_path='v4_uuids.csv',
    input_svg_path='calibration_page-coloured.svg',
    output_filename='document_001'  # Customize this name
)

if result:
    uuid, output_path = result
    print(f"✓ Document signed successfully!")
    print(f"  UUID: {uuid}")
    print(f"  Output file: {output_path}")
    print(f"  CSV updated: entity={output_path}, state=active")
else:
    print("✗ No available UUID found in the CSV file")

