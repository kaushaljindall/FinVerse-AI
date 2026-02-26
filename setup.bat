python -m venv venv
call venv\Scripts\activate.bat
pip install -r backend\requirements.txt
python backend\scripts\index_documents.py
