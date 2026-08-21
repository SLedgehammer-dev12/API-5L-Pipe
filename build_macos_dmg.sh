#!/usr/bin/env bash
# ======================================================================
# macOS Standalone Application (.app) & Disk Image (.dmg) Builder
# Clean, isolated build optimized for Apple Silicon (M1/M2/M3/M4) & Intel
# ======================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

APP_NAME="API-5L-Pipe"
VERSION="1.0.0"
DMG_NAME="${APP_NAME}-v${VERSION}-macOS.dmg"
DIST_DIR="$DIR/dist"
BUILD_DIR="$DIR/build"

echo "======================================================================"
echo "  📦 Building macOS .app and .dmg for ${APP_NAME} v${VERSION}"
echo "  💻 Architecture: $(uname -m)"
echo "======================================================================"

# Build .app bundle using PyInstaller without UPX (UPX triggers false antivirus heuristics)
echo "🔨 Compiling standalone binary..."
pyinstaller \
    --name "${APP_NAME}" \
    --windowed \
    --noconfirm \
    --noupx \
    --workpath "$BUILD_DIR" \
    --distpath "$DIST_DIR" \
    --specpath "$BUILD_DIR" \
    --add-data "static:static" \
    --add-data "templates:templates" \
    --add-data "core:core" \
    --hidden-import "uvicorn" \
    --hidden-import "uvicorn.logging" \
    --hidden-import "uvicorn.loops" \
    --hidden-import "uvicorn.loops.auto" \
    --hidden-import "uvicorn.protocols" \
    --hidden-import "uvicorn.protocols.http" \
    --hidden-import "uvicorn.protocols.http.auto" \
    --hidden-import "uvicorn.lifespan" \
    --hidden-import "uvicorn.lifespan.on" \
    --hidden-import "fastapi" \
    --hidden-import "openpyxl" \
    --hidden-import "jinja2" \
    --hidden-import "pydantic" \
    run.py

echo "🔏 Applying local ad-hoc code signature for clean execution..."
if [ -d "$DIST_DIR/${APP_NAME}.app" ]; then
    codesign --force --deep -s - "$DIST_DIR/${APP_NAME}.app" || true
fi

echo "💿 Creating Apple Disk Image (.dmg)..."
mkdir -p "$DIST_DIR/dmg_root"
cp -R "$DIST_DIR/${APP_NAME}.app" "$DIST_DIR/dmg_root/"
ln -s /Applications "$DIST_DIR/dmg_root/Applications"

hdiutil create -volname "${APP_NAME} v${VERSION}" \
    -srcfolder "$DIST_DIR/dmg_root" \
    -ov -format UDZO \
    "$DIST_DIR/$DMG_NAME"

rm -rf "$DIST_DIR/dmg_root"

echo "======================================================================"
echo "✅ macOS .dmg Package Created Successfully!"
echo "📍 Location: $DIST_DIR/$DMG_NAME"
echo "======================================================================"
