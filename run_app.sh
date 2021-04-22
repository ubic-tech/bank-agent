docker run -d -p 27017:27017 --name mongodb_a mongo:4.0.4
env MONGO_PORT=27017 BANK_UUID=111aaaaa-1af0-489e-b761-d40344c12e70 uvicorn main:app --host 0.0.0.0 --port 8081 --reload