#!/bin/bash
set -e

echo "🔧 Compilation de la bibliothèque Rust..."
cd libs/rustlib
cargo build --release

echo "📁 Copie des bibliothèques compilées..."
# Copier les fichiers selon l'OS
if [ -f "target/release/librustlib.so" ]; then
    cp target/release/librustlib.so ../librustlib.so
    echo "✅ Bibliothèque Linux copiée (librustlib.so)"
elif [ -f "target/release/librustlib.dylib" ]; then
    cp target/release/librustlib.dylib ../librustlib.dylib
    echo "✅ Bibliothèque macOS copiée (librustlib.dylib)"
elif [ -f "target/release/librustlib.dll" ]; then
    cp target/release/librustlib.dll ../librustml.dll
    echo "✅ Bibliothèque Windows copiée (librustml.dll)"
else
    echo "❌ Aucune bibliothèque trouvée dans target/release/"
    ls -la target/release/
    exit 1
fi

cd ../..

echo "📦 Installation des dépendances Python..."
pip3 install -r requirements.txt

echo "🚀 Lancement de l'API FastAPI..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
