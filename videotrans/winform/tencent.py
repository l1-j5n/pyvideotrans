from videotrans.configure import config


def open():
    def save():
        SecretId = tencentw.tencent_SecretId.text()
        SecretKey = tencentw.tencent_SecretKey.text()
        config.params["tencent_SecretId"] = SecretId
        config.params["tencent_SecretKey"] = SecretKey
        config.getset_params(config.params)
        tencentw.close()

    from videotrans.component import TencentForm
    tencentw = config.child_forms.get('tencentw')
    if tencentw is not None:
        tencentw.show()
        tencentw.raise_()
        tencentw.activateWindow()
        return
    tencentw = TencentForm()
    config.child_forms['tencentw'] = tencentw
    if config.params["tencent_SecretId"]:
        tencentw.tencent_SecretId.setText(config.params["tencent_SecretId"])
    if config.params["tencent_SecretKey"]:
        tencentw.tencent_SecretKey.setText(config.params["tencent_SecretKey"])
    tencentw.set_tencent.clicked.connect(save)
    tencentw.show()
