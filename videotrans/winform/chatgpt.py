import builtins
import json
import os

from PySide6 import QtWidgets
from PySide6.QtCore import QThread, Signal

from videotrans.configure import config

# 使用内置的 open 函数
builtin_open = builtins.open


# set chatgpt
def open():
    class TestChatgpt(QThread):
        uito = Signal(str)

        def __init__(self, *, parent=None):
            super().__init__(parent=parent)

        def run(self):
            try:
                from videotrans.translator.chatgpt import trans as trans_chatgpt
                raw = "你好啊我的朋友" if config.defaulelang != 'zh' else "hello,my friend"
                text = trans_chatgpt(raw, "English" if config.defaulelang != 'zh' else "Chinese", set_p=False,
                                     is_test=True)
                self.uito.emit(f"ok:{raw}\n{text}")
            except Exception as e:
                self.uito.emit(str(e))

    def feed(d):
        if not d.startswith("ok:"):
            QtWidgets.QMessageBox.critical(chatgptw, config.transobj['anerror'], d)
        else:
            QtWidgets.QMessageBox.information(chatgptw, "OK", d[3:])
        chatgptw.test_chatgpt.setText('测试' if config.defaulelang == 'zh' else 'Test')

    def test():
        key = chatgptw.chatgpt_key.text()
        api = chatgptw.chatgpt_api.text().strip()
        api = api if api else 'https://api.openai.com/v1'
        model = chatgptw.chatgpt_model.currentText()
        template = chatgptw.chatgpt_template.toPlainText()

        os.environ['OPENAI_API_KEY'] = key
        config.params["chatgpt_key"] = key
        config.params["chatgpt_api"] = api
        config.params["chatgpt_model"] = model
        config.params["chatgpt_template"] = template

        task = TestChatgpt(parent=chatgptw)
        chatgptw.test_chatgpt.setText('测试中请稍等...' if config.defaulelang == 'zh' else 'Testing...')
        task.uito.connect(feed)
        task.start()
        chatgptw.test_chatgpt.setText('测试中请稍等...' if config.defaulelang == 'zh' else 'Testing...')

    def save_chatgpt():
        key = chatgptw.chatgpt_key.text()
        api = chatgptw.chatgpt_api.text().strip()
        api = api if api else 'https://api.openai.com/v1'
        model = chatgptw.chatgpt_model.currentText()
        template = chatgptw.chatgpt_template.toPlainText()

        with builtin_open(config.ROOT_DIR + f"/videotrans/chatgpt{'-en' if config.defaulelang != 'zh' else ''}.txt",
                          'w',
                          encoding='utf-8') as f:
            f.write(template)
        os.environ['OPENAI_API_KEY'] = key
        config.params["chatgpt_key"] = key
        config.params["chatgpt_api"] = api
        config.params["chatgpt_model"] = model
        config.params["chatgpt_template"] = template
        config.getset_params(config.params)
        chatgptw.close()

    def setallmodels():
        t = chatgptw.edit_allmodels.toPlainText().strip().replace('，', ',').rstrip(',')
        current_text = chatgptw.chatgpt_model.currentText()
        chatgptw.chatgpt_model.clear()
        chatgptw.chatgpt_model.addItems([x for x in t.split(',') if x.strip()])
        if current_text:
            chatgptw.chatgpt_model.setCurrentText(current_text)
        config.settings['chatgpt_model'] = t
        json.dump(config.settings, builtin_open(config.ROOT_DIR + '/videotrans/cfg.json', 'w', encoding='utf-8'),
                  ensure_ascii=False)

    def update_ui():
        config.settings = config.parse_init()
        allmodels_str = config.settings['chatgpt_model']
        allmodels = config.settings['chatgpt_model'].split(',')
        chatgptw.chatgpt_model.clear()
        chatgptw.chatgpt_model.addItems(allmodels)
        chatgptw.edit_allmodels.setPlainText(allmodels_str)

        if config.params["chatgpt_key"]:
            chatgptw.chatgpt_key.setText(config.params["chatgpt_key"])
        if config.params["chatgpt_api"]:
            chatgptw.chatgpt_api.setText(config.params["chatgpt_api"])
        if config.params["chatgpt_model"] and config.params['chatgpt_model'] in allmodels:
            chatgptw.chatgpt_model.setCurrentText(config.params["chatgpt_model"])
        if config.params["chatgpt_template"]:
            chatgptw.chatgpt_template.setPlainText(config.params["chatgpt_template"])

    from videotrans.component import ChatgptForm
    chatgptw = config.child_forms.get('chatgptw')
    if chatgptw is not None:
        chatgptw.show()
        update_ui()
        chatgptw.raise_()
        chatgptw.activateWindow()
        return
    chatgptw = ChatgptForm()
    config.child_forms['chatgptw'] = chatgptw
    update_ui()
    chatgptw.set_chatgpt.clicked.connect(save_chatgpt)
    chatgptw.test_chatgpt.clicked.connect(test)
    chatgptw.edit_allmodels.textChanged.connect(setallmodels)
    chatgptw.show()
