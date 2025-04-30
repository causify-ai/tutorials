#!/bin/bash

# Ensure we're in the current directory
cd "$(dirname "$0")"

# Rename API file if needed
if [ -f "template.API.py" ]; then
  mv template.API.py template_API.py
fi

# Overwrite template.example.py with correct uvicorn call
cat > template.example.py <<EOF
import uvicorn

if __name__ == "__main__":
    uvicorn.run("template_API:app", host="127.0.0.1", port=8080, reload=True)
EOF

# Run the FastAPI server using template.example.py
python3 template.example.py
