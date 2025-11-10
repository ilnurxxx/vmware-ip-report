import logging
from pyVmomi import vim

# Setup logger
logger = logging.getLogger(__name__)


def process_vm(vm_obj, host_pg_dict, dvpg_dict):
    """
    Обработка информации о ВМ и подготовка сетевого отчета 
    """
    try:
        if not hasattr(vm_obj, 'propSet') or not vm_obj.propSet:
            return None
        props = {p.name: p.val for p in vm_obj.propSet}
        if not props.get("config.instanceUuid"):
            return None

        name = props["name"]
        power_state = "ON" if "poweredOn" in str(props["runtime.powerState"]) else "OFF"
        instance_uuid = props["config.instanceUuid"]

        # Guest info (vmware tools): список IP + link status по mac
        guest_nics = {}
        guest_net = props.get("guest.net")
        if guest_net:
            for gnic in guest_net:
                ips_v4 = [ip for ip in (gnic.ipAddress or []) if ':' not in ip and ip != '0.0.0.0']
                mac = gnic.macAddress.lower() if gnic.macAddress else None
                if mac:
                    guest_nics[mac] = {
                        'ips': ips_v4,
                        'connected': gnic.connected
                    }

        # NICs (сетевые интерфейсы)
        nic_infos = []
        devices = props.get("config.hardware.device", [])
        host = props.get("runtime.host")

        for dev in devices:
            if not isinstance(dev, vim.vm.device.VirtualEthernetCard):
                continue

            mac = dev.macAddress.lower() if dev.macAddress else None
            connected_config = dev.connectable.connected if dev.connectable else False

            # получаем имя сети с интерфейса
            pg_name = "no_network"
            if isinstance(dev.backing, vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo):
                port = dev.backing.port
                dvpg = dvpg_dict.get(port.portgroupKey)
                if dvpg:
                    pg_name = dvpg.name
            elif isinstance(dev.backing, vim.vm.device.VirtualEthernetCard.NetworkBackingInfo):
                pg_name = dev.backing.deviceName

            # получаем IP и link status
            gnic = guest_nics.get(mac, {})
            ips = gnic.get('ips', [])
            ips = sorted(ips, key=lambda x: tuple(int(p) for p in x.split('.')))
            connected = gnic.get('connected', connected_config)
            status = 'up' if connected else 'down'

            # форматирование каждого IP в отдельную строку
            if ips:
                for ip in ips:
                    nic_infos.append(f"{ip} ({pg_name} {status})")
            else:
                nic_infos.append(f"no_ip ({pg_name} {status})")

        network_info = ";\n".join(nic_infos) if nic_infos else "no networks"

        return {
            "instanceUuid": instance_uuid,
            "Name": name,
            "Power State": power_state,
            "Network Info": network_info
        }

    except Exception as e:
        logger.warning(f"Ошибка обработки ВМ {getattr(vm_obj, 'name', 'unknown')}: {e}")
        return {
            "instanceUuid": "ERROR",
            "Name": getattr(vm_obj, 'name', 'unknown'),
            "Power State": "ERROR",
            "Network Info": f"ERROR: {e}"
        }