import logging
from pyVmomi import vim, vmodl
from tqdm import tqdm

# Setup logger
logger = logging.getLogger(__name__)


def get_properties(content):
    """
    Получение ContainerView и выборка нужных полей через PropertyCollector
    """
    view = content.viewManager.CreateContainerView(
        content.rootFolder, [vim.VirtualMachine], True
    )

    # Список нужных полей
    property_specs = [
        vmodl.query.PropertyCollector.PropertySpec(
            type=vim.VirtualMachine,
            pathSet=[
                "name",
                "runtime.powerState",
                "config.instanceUuid",
                "guest.net",
                "config.hardware.device",
                "runtime.host"
            ]
        )
    ]

    obj_specs = [
        vmodl.query.PropertyCollector.ObjectSpec(obj=vm) for vm in view.view
    ]

    filter_spec = vmodl.query.PropertyCollector.FilterSpec(
        objectSet=obj_specs,
        propSet=property_specs
    )

    results = content.propertyCollector.RetrieveContents([filter_spec])
    view.Destroy()
    logger.info(f"Сформирован ContainerView, количество хостов: {len(results)}")
    return results


def collect_portgroups(content):
    """
    Создание кэша портгрупп standart switch (vSS)
    """
    view = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
    hosts = view.view
    host_pg_dict = {}
    for host in hosts:
        host_pg_dict[host] = {pg.spec.name: pg for pg in host.config.network.portgroup}
    view.Destroy()
    logger.debug(f"Создан кэш vSS, количество записей: {sum(len(d) for d in host_pg_dict.values())}")
    return host_pg_dict


def collect_dvpgs(content):
    """
    Создание кэша портгрупп distributed switch (vDS)
    """
    view = content.viewManager.CreateContainerView(content.rootFolder, [vim.dvs.DistributedVirtualPortgroup], True)
    dvpgs = view.view
    dvpg_dict = {pg.key: pg for pg in dvpgs}
    view.Destroy()
    logger.debug(f"Создан кэш vDS, количество записей: {len(dvpg_dict)}")
    return dvpg_dict