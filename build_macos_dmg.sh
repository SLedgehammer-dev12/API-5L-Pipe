#!/usr/bin/env bash
# ======================================================================
# macOS Standalone Application (.app) & Disk Image (.dmg) Builder
# Clean, isolated build optimized for Apple Silicon (M1/M2/M3/M4) & Intel
# ======================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

APP_NAME="API-5L-Pipe"
VERSION="$(python3 -c 'from version import __version__; print(__version__)' 2>/dev/null || echo "0.0.0")"
DMG_NAME="${APP_NAME}-macOS-v${VERSION}.dmg"
DIST_DIR="$DIR/dist"
BUILD_DIR="$DIR/build"

echo "======================================================================"
echo "  📦 Building macOS .app and .dmg for ${APP_NAME} v${VERSION}"
echo "  💻 Architecture: $(uname -m)"
echo "======================================================================"

export KIVY_NO_CONFIG=1
export KIVY_NO_FILELOG=1

# Build .app bundle using PyInstaller without UPX (UPX triggers false antivirus heuristics)
echo "🔨 Compiling standalone binary..."
pyinstaller \
    --name "${APP_NAME}-macOS-v${VERSION}" \
    --windowed \
    --noconfirm \
    --noupx \
    --icon "$DIR/static/icon/app_icon.icns" \
    --workpath "$BUILD_DIR" \
    --distpath "$DIST_DIR" \
    --specpath "$BUILD_DIR" \
    --add-data "$DIR/static:static" \
    --add-data "$DIR/templates:templates" \
    --add-data "$DIR/core:core" \
    --hidden-import "app" \
    --hidden-import "core" \
    --hidden-import "core.database" \
    --hidden-import "core.pipe_qaqc_engine" \
    --hidden-import "core.verification_engine" \
    --hidden-import "core.wall_thickness_engine" \
    --hidden-import "core.project_manager" \
    --hidden-import "core.updater" \
    --hidden-import "core.excel_exporter" \
    --hidden-import "core.i18n" \
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
    --hidden-import "core.pdf_exporter" \
    --hidden-import "core.unlimited_ocr_engine" \
    --hidden-import "core.itp_audit_engine" \
    --hidden-import "core.itp_criteria_parser" \
    --hidden-import "core.sawh_engine" \
    --collect-all reportlab \
    --collect-all fitz \
    --collect-all httpx \
    --collect-all anyio \
    --collect-all httpcore \
    --collect-all certifi \
    --hidden-import truststore \
    --hidden-import "version" \
    run.py

echo "🔏 Applying local ad-hoc code signature for clean execution..."
APP_BUNDLE="$DIST_DIR/${APP_NAME}-macOS-v${VERSION}.app"
if [ -d "$APP_BUNDLE" ]; then
    codesign --force --deep -s - "$APP_BUNDLE" || true
fi

echo "💿 Creating Apple Disk Image (.dmg)..."
mkdir -p "$DIST_DIR/dmg_root"
cp -R "$APP_BUNDLE" "$DIST_DIR/dmg_root/"
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