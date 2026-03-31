# Лабораторная работа 1: Docker (Advanced-трек)

## Ход выполнения
Перед выполнением лабораторной я подготовила среду в виртуальной машине Ubuntu: проверела наличие Python и прав sudo, создала директорию `lab1-docker`, скачала и распаковала rootfs Alpine

Дальше я создала `config.json`
```
{
  "ociVersion": "1.0.2",
  "hostname": "lab1-container",
  "root": {
    "path": "/home/alisa/devops/lab1-docker/alpine-rootfs"
  },
  "process": {
    "cwd": "/",
    "env": [
      "PATH=/bin:/sbin:/usr/bin:/usr/sbin"
    ],
    "args": ["/bin/sh"]
  }
}
```



## Тестирование

Дальше я протестировала работу программы. Запустила ее командой `sudo ./minioci.py c1 config.json` и выполнила следующие проверки:
- `hostname` внутри контейнера
- PID namespace: `echo $$`
- rootfs: `cat /etc/os-release`
- /proc: `ps`
- директории контейнера: `sudo ls -R /var/lib/minioci/c1`
- overlayfs: `echo "hello from container" > /testfile` и `sudo find /var/lib/minioci/c1/upper -name testfile`

![test](test.png)
