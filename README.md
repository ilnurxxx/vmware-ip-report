# VMWare IP Report

**Сбор инвентаризационной информации о ВМ с vCenter: IP-адреса, название сетей и статусы.**  
**Функционал проекта аналогичен vNetworkInfo в RVTools, но с возможность запуска на всех ОС (RVTools только под Windows)**

## Особенности

- **1 запрос** на 1000+ ВМ (используется `PropertyCollector`)
- **Кэширование** PortGroups (vSS + DVS)
- **IP-адреса в читаемом формате** как для ручного исследования, так и для использования в других системах (например GLPI)
- **Имя сети - как в vCenter (Network Name)**
- **JSON в stdout** для API

## Установка

```bash
git clone https://github.com/ilnurxxx/vmware-ip-report.git
cd vmware-ip-report

# Установка
pip install -r requirements.txt

# Конфигурация
cp config/.env.example config/.env
nano config/.env
```

## Пример config/.env
```bash
VCSA_HOST=vcsa.example.com
VCSA_PORT=443
VCSA_USER=administrator@vsphere.local
VCSA_PASS=YourStrongPass!
```

## Использование

### Quiet Mode 
Отображение только критичных логов

```bash
python main.py --quiet 
```

### Excel
```bash
python main.py --get-excel
```

### CSV
```bash
python main.py --get-csv
```

### JSON (для API, Ansible, Python)
```bash
python main.py --get-json
```

### JSON для N8N с параметром status (можно использовать в IF-Node)
```bash
python main.py --get-json-n8n
```

## Пример вывода
```json
[
  {
    "instanceUuid": "123abc...",
    "Name": "Vm-Name01",
    "Power State": "ON",
    "Network Info": "192.168.1.2 (local-vlan1 up);\n 10.0.0.2 (local-vlan2 up);\nno_ip (ext-vlan3 down)" # IP_address (network_name link_status)
  }
]
```

