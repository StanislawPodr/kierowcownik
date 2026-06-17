#!/bin/bash
set -e

mkdir -p /app/data

echo "Applying database migrations..."
python manage.py migrate --noinput

XLSX_FILE=${DATA_XLSX:-"/app/import/questions.xlsx"}
ZIPS_FILES=${RESOURCES_ZIP:-"/app/import/resources.zip"}

if [ -n "$ZIPS_FILES" ]; then
    ARE_FILES=1
    for f in $ZIPS_FILES; do
        if [ ! -f "$f" ]; then
            echo "File $f not found. Skipping extraction."
            ARE_FILES=0
        fi
    done
    test "$ARE_FILES" -eq "1" && python manage.py add_resources --reset $ZIPS_FILES
fi

if [ -f "$XLSX_FILE" ]; then
    echo "Found questions file at $XLSX_FILE. Parsing..."
    python manage.py parse_questions --reset "$XLSX_FILE"
else
    echo "Questions file not found at $XLSX_FILE. Skipping parsing."
fi

echo "Starting application..."
exec "$@"
