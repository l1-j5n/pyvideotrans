import time

from PySide6.QtCore import QThread

from videotrans.configure import config
from videotrans.util.tools import set_process


class WorkerRegcon(QThread):
    def __init__(self, *, parent=None):
        super().__init__(parent=parent)

    def run(self) -> None:
        while 1:
            if config.exit_soft:
                return
            if len(config.regcon_queue) < 1:
                time.sleep(0.5)
                continue
            trk = config.regcon_queue.pop(0)
            try:
                trk.recogn()
                # 插入翻译队列
                config.trans_queue.append(trk)
            except Exception as e:
                if trk.uuid not in config.uuidlist:
                    config.uuidlist.append(trk.uuid)
                config.logger.exception(e)
                set_process(f'{config.transobj["shibiechucuo"]}:' + str(e), type='error', uuid=trk.uuid)


class WorkerTrans(QThread):
    def __init__(self, *, parent=None):
        super().__init__(parent=parent)

    def run(self) -> None:
        while 1:
            if config.exit_soft:
                return
            if len(config.trans_queue) < 1:
                time.sleep(0.5)
                continue
            trk = config.trans_queue.pop(0)
            try:
                trk.trans()
                config.dubb_queue.append(trk)
            except Exception as e:
                if trk.uuid not in config.uuidlist:
                    config.uuidlist.append(trk.uuid)
                msg = f'{config.transobj["fanyichucuo"]}:' + str(e)
                config.logger.exception(e)
                set_process(msg, type='error', uuid=trk.uuid)


class WorkerDubb(QThread):
    def __init__(self, *, parent=None):
        super().__init__(parent=parent)

    def run(self) -> None:
        while 1:
            if config.exit_soft:
                return
            if len(config.dubb_queue) < 1:
                time.sleep(0.5)
                continue
            trk = config.dubb_queue.pop(0)
            try:
                trk.dubbing()
                config.align_queue.append(trk)
            except Exception as e:
                if trk.uuid not in config.uuidlist:
                    config.uuidlist.append(trk.uuid)
                msg = f'{config.transobj["peiyinchucuo"]}:' + str(e)
                config.logger.exception(e)
                set_process(msg, type='error', uuid=trk.uuid)


class WorkerAlign(QThread):
    def __init__(self, *, parent=None):
        super().__init__(parent=parent)

    def run(self) -> None:
        while 1:
            if config.exit_soft:
                return
            if len(config.align_queue) < 1:
                time.sleep(0.5)
                continue
            trk = config.align_queue.pop(0)
            try:
                trk.align()
                config.compose_queue.append(trk)
            except Exception as e:
                if trk.uuid not in config.uuidlist:
                    config.uuidlist.append(trk.uuid)
                msg = f'{config.transobj["peiyinchucuo"]}:' + str(e)
                config.logger.exception(e)
                set_process(msg, type='error', uuid=trk.uuid)


class WorkerCompose(QThread):
    def __init__(self, *, parent=None):
        super().__init__(parent=parent)

    def run(self) -> None:
        while 1:
            if config.exit_soft:
                return
            if len(config.compose_queue) < 1:
                time.sleep(0.5)
                continue
            trk = config.compose_queue.pop(0)
            try:
                trk.hebing()
                trk.move_at_end()
            except Exception as e:
                msg = f'{config.transobj["hebingchucuo"]}:' + str(e)
                config.logger.exception(e)
                set_process(msg, type='error', uuid=trk.uuid)
            finally:
                if trk.uuid not in config.uuidlist:
                    config.uuidlist.append(trk.uuid)


def start_thread(parent):
    regcon_thread = WorkerRegcon(parent=parent)
    regcon_thread.start()
    trans_thread = WorkerTrans(parent=parent)
    trans_thread.start()
    dubb_thread = WorkerDubb(parent=parent)
    dubb_thread.start()
    align_thread = WorkerAlign(parent=parent)
    align_thread.start()
    compose_thread = WorkerCompose(parent=parent)
    compose_thread.start()
