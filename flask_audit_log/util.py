import importlib
import logging


def get_client_ip(request) -> str:
    try:
        # Get the ip address from x-forwarded-for or use the remote_addr
        return request.headers.getlist("X-Forwarded-For")[0] if request.headers.getlist("X-Forwarded-For") \
                                                           else request.remote_addr
    except Exception:
        logger = logging.getLogger(__name__)
        logger.warning('Failed to get ip for audit log', exc_info=True)
        return 'failed to get ip'


def import_callable(path):
    module, method = path.rsplit('.', 1)
    return getattr(importlib.import_module(module), method)
