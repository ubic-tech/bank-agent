#### Переменные окружения

* UBIC_URL: путь к Ubic-MPC, например: `http://0.0.0.0:8888`

* MONGO_HOST: адрес MongoDB

* MONGO_PORT порт MongoDB (по умолчанию `27017`)

* BANK_UUID уникальный индетификатор участника MPC

* COMPUTE_TIMEOUT максимальное время (c) ожидания результата

#### команды запуска системы из 3 участников MPC:

* запуск 3ёх контейнеров MongoDB:
  ```
  docker run -d -p 27017:27017 --name mongodb_a mongo:4.0.4 
  docker run -d -p 27018:27017 --name mongodb_a mongo:4.0.4
  docker run -d -p 27019:27017 --name mongodb_a mongo:4.0.4
  ```

* установка зависимостей:

`pip install -r requirements.txt`

* запуск 3ёх участников MPC:

```
env MONGO_PORT=27017 BANK_UUID=111aaaaa-1af0-489e-b761-d40344c12e70 uvicorn main:app --host 0.0.0.0 --port 8081
env MONGO_PORT=27018 BANK_UUID=222aaaaa-1af0-489e-b761-d40344c12e70 uvicorn main:app --host 0.0.0.0 --port 8082
env MONGO_PORT=27019 BANK_UUID=333aaaaa-1af0-489e-b761-d40344c12e70 uvicorn main:app --host 0.0.0.0 --port 8083
```


* либо использовать `Dockerfile`, кастомизируя переменные среды и параметры запуска
  

* запуск Ubic-stub:

```
git clone https://gitlab.ubic.tech/datahub/banks-mpc/common.git
cd common
uvicorn main:app --host 0.0.0.0 --port 8888
```

* запуск вычислений:

POST запрос по адресу: `http://0.0.0.0:8081/v1/compute`

c телом:
```
{
    "clients": [
        "aaa1fc87-5722-4383-9830-2be483b6468d",
        "bbb1fc87-5722-4383-9830-2be483b6468d",
        "ccc1fc87-5722-4383-9830-2be483b6468d",
        "eee1fc87-5722-4383-9830-2be483b6468d",
        "aba1fc87-5722-4383-9830-2be483b6468d"
    ]
}
```


