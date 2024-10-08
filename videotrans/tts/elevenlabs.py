import json
import os

from elevenlabs import generate, Voice, set_api_key

from videotrans.configure import config
from videotrans.util import tools

shound_del = False


def update_proxy(type='set'):
    global shound_del
    if type == 'del' and shound_del:
        del os.environ['http_proxy']
        del os.environ['https_proxy']
        del os.environ['all_proxy']
        shound_del = False
    elif type == 'set':
        raw_proxy = os.environ.get('http_proxy')
        if not raw_proxy:
            proxy = tools.set_proxy()
            if proxy:
                shound_del = True
                os.environ['http_proxy'] = proxy
                os.environ['https_proxy'] = proxy
                os.environ['all_proxy'] = proxy


def get_voice(*, text=None, role=None, volume="+0%", pitch="+0Hz", rate=None, language=None, filename=None, set_p=True,
              inst=None, uuid=None):
    try:
        update_proxy(type='set')
        with open(os.path.join(config.ROOT_DIR, 'elevenlabs.json'), 'r', encoding="utf-8") as f:
            jsondata = json.loads(f.read())
        if config.params['elevenlabstts_key']:
            set_api_key(config.params['elevenlabstts_key'])
        audio = generate(
            text=text,
            voice=Voice(voice_id=jsondata[role]['voice_id']),
            model="eleven_multilingual_v2"
        )
        with open(filename, 'wb') as f:
            f.write(audio)
        if tools.vail_file(filename) and config.settings['remove_silence']:
            tools.remove_silence_from_end(filename)
        if set_p:
            if inst and inst.precent < 80:
                inst.precent += 0.1
            tools.set_process(f'{config.transobj["kaishipeiyin"]} ', uuid=uuid)
    except ConnectionError as e:
        raise Exception(str(e))
    except Exception as e:
        error = str(e)
        if set_p:
            tools.set_process(f'elevenlabs:{error}', uuid=uuid)
        config.logger.error(f"elevenlabsTTS：request error:{error}")
        raise
    finally:
        if shound_del:
            update_proxy(type='del')
    return True
