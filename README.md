# Yosr Website
1. download needed dependencies from `requirements.txt`
2. in one terminal run the backend and in the other run the frontend from the `command.txt` file

*Note* you have to ctr+c and rerun each time you make a change, refreshing isn't enough
# How to run the backend Server
1. Start the  FastAPI server (Terminal 1)
  ```bash
  cd backend
  uvicorn main:app --reload
```   
2. Run the website (Terminal 2)
   ```bash
   cd frontend
   python main.py
   ```
