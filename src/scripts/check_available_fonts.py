import fitz  # PyMuPDF
import os
import sys

# Test that script is running
print("Script started...", file=sys.stderr, flush=True)
print("PyMuPDF version:", fitz.version, file=sys.stderr, flush=True)

def check_font_availability(font_name):
    """Check if a font is available in PyMuPDF by trying to use it."""
    try:
        doc = fitz.open()
        page = doc.new_page()
        # Try to insert text with the font
        try:
            page.insert_text((10, 10), "Test", fontname=font_name, fontsize=12)
            result = True
        except Exception as e:
            result = False
        finally:
            doc.close()
        return result
    except Exception as e:
        return False

def get_windows_fonts():
    """Get list of installed fonts on Windows."""
    fonts = []
    font_dirs = [
        os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'Fonts'),
    ]
    
    for font_dir in font_dirs:
        if os.path.exists(font_dir):
            try:
                for file in os.listdir(font_dir):
                    if file.lower().endswith(('.ttf', '.otf', '.ttc')):
                        # Remove extension and add to list
                        font_name = os.path.splitext(file)[0]
                        fonts.append((font_name, os.path.join(font_dir, file)))
            except:
                pass
    
    return fonts

try:
    print("=== Checking Available Fonts ===", flush=True)
    print("\n1. Testing common font names in PyMuPDF:", flush=True)

    # Common fonts to test
    test_fonts = [
        'helv', 'tiro', 'cour', 'times', 'symb', 'zapf', 'webdings',
        'Arial', 'Times-Roman', 'Courier', 'Helvetica', 'Symbol', 'Webdings',
        'Calibri', 'Verdana', 'Tahoma', 'Comic Sans MS'
    ]

    available_fonts = []
    for font in test_fonts:
        if check_font_availability(font):
            available_fonts.append(font)
            print(f"  ✓ {font}", flush=True)

    print(f"\n   Found {len(available_fonts)} working fonts out of {len(test_fonts)} tested", flush=True)

    # Check Webdings specifically
    print("\n2. Checking for Webdings:", flush=True)
    webdings_variants = ['webdings', 'Webdings', 'WEBDINGS']
    webdings_found = False
    for variant in webdings_variants:
        if check_font_availability(variant):
            print(f"  ✓ {variant} is available", flush=True)
            webdings_found = True

    if not webdings_found:
        print("  ✗ Webdings not found using standard font names", flush=True)

    # Check system fonts on Windows
    if sys.platform == 'win32':
        print("\n3. Checking Windows system fonts:", flush=True)
        windows_fonts = get_windows_fonts()
        webdings_files = [f for f in windows_fonts if 'webding' in f[0].lower()]
        
        if webdings_files:
            print(f"  Found {len(webdings_files)} Webdings font file(s):", flush=True)
            for name, path in webdings_files:
                print(f"    - {name} ({path})", flush=True)
        else:
            print("  No Webdings font files found in Windows Fonts directory", flush=True)
        
        # Try testing the actual font file path
        if webdings_files:
            print("\n4. Testing Webdings font file directly:", flush=True)
            for name, path in webdings_files:
                # PyMuPDF might accept font file paths in some contexts
                # but typically we need to use font names, not paths
                print(f"  Note: Font file exists at {path}", flush=True)
                print(f"  You may need to use the font name '{name}' or install it properly", flush=True)

    print("\n=== Note ===", flush=True)
    print("PyMuPDF uses font names (like 'webdings' or 'helv'), not file paths.", flush=True)
    print("If a font is installed but not working, try different name variations.", flush=True)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr, flush=True)
    import traceback
    traceback.print_exc()