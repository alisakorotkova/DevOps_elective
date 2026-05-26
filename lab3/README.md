# Лабораторная работа 3: nginx (базовый-трек)

## Ход выполнения

### Часть 1

Для начала выполнения работы я установила nginx и mkcert, чтобы создать локальный HTTPS-сертификат:

![test](content/instal_ng.png)
![test](content/inst_cert.png)

Создала 2 проекта:

Для работы HTTPS был создала локальный сертификат с помощью mkcert:
```
mkcert \
  -cert-file ~/nginx-lab/certs/lab.crt \
  -key-file ~/nginx-lab/certs/lab.key \
  project1.test project2.test
```
![test](content/cert.png)

И в результате были получила два файла `lab.crt` и `lab.key`.

**Далее я настроила конфиг:**

```
    #Перенаправление HTTP на HTTPS
    server {
        listen 80;
        server_name project1.test project2.test;

        return 301 https://$host$request_uri;
    }

    #Первый виртуальный хост
    server {
        listen 443 ssl;
        server_name project1.test;

        ssl_certificate     /opt/homebrew/var/www/nginx-lab/certs/lab.crt;
        ssl_certificate_key /opt/homebrew/var/www/nginx-lab/certs/lab.key;

        root /opt/homebrew/var/www/nginx-lab/project1;
        index index.html;

        location / {
            try_files $uri $uri/ =404;
        }

        # alias:
        location /shared/ {
            alias /opt/homebrew/var/www/nginx-lab/shared/;
        }
    }

    #Второй виртуальный хост
    server {
        listen 443 ssl;
        server_name project2.test;

        ssl_certificate     /opt/homebrew/var/www/nginx-lab/certs/lab.crt;
        ssl_certificate_key /opt/homebrew/var/www/nginx-lab/certs/lab.key;

        root /opt/homebrew/var/www/nginx-lab/project2;
        index index.html;

        location / {
            try_files $uri $uri/ =404;
        }

        # alias:
        location /shared/ {
            alias /opt/homebrew/var/www/nginx-lab/shared/;
        }
    }
```

**Дальше я проверила работоспособность:**

Проверка конфигурации nginx
![test](content/nginxt-t.png)

Проверка работы HTTPS
![test](content/curl-k-i.png)

Проверка редиректа HTTP на HTTPS
![test](content/curl-i.png)

Доступ к project1 `http://project1.test`
![test](content/pr1.png)

Доступ к project2 `http://project2.test`
![test](content/pr2.png)

Проверка alias `https://project1.test/shared/info.txt`
![test](content/shrd.png)

Таким образом, nginx был настроен по тз: он работает по HTTPS, перенаправляет HTTP на HTTPS, обслуживает несколько доменных имен и использует alias для переопределения путей к файлам.




