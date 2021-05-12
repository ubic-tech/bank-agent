### Запуск системы из 3 участников MPC:

`./create_image.sh`

`docker-compose up`

### Пример запроса совокупного баланса:

POST запрос по адресу: `http://localhost:9091/v1/compute`

c телом:
```
{
    "clients": [
        "bd2e86ce81ae00d65c2c02074a1e85c0a483613c74760f22f1fc07080d6e5dc5",
        "9c2d29850e7fd884c19b3ef48a01b82c0a88854082ad150056ac770dcbeee05c",
        "1a5d06a170dde413475957ca2b63396aa5e8fbecb7d379fcb668da3753fca5b6"
    ]
}
```

### Кастомизация балансов

В файле `repository/fake_repository.py` находится словарь клиентов `_clients`, который выполняет роль БД с балансами.

Чтобы изменить баланс клиентов, необходимо внести изменения в `_clients`. Также можно добавить новых клиентов.

#### Пример изменения баланса для клиента

```
 _bank_a: {
-    _oleg: 199,        # было
+    _oleg: 100500,     # стало
     _olga: 102,
```

В вышеприведенном примере баланс клиента `_oleg` в банке `_bank_a` был изменён со `199` на `100500`. 