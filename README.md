# Windows 实时变声器（Python）

> 说明：本项目提供实时变声能力（变调、机器人音色、低沉音色）。
>
> 不提供对特定真人（包括公众人物）的声音克隆模型。若你有**合法授权**的目标音色模型，可在本项目中替换处理器。

## 功能

- 麦克风实时输入，扬声器实时输出
- 3 种可切换音色：
  - `pitch_up`：更高音色（常用于女声化）
  - `pitch_down`：更低音色（常用于男声化）
  - `robot`：机器人感
- 可调参数：采样率、块大小、音量

## 环境

- Windows 10/11
- Python 3.10+
- 建议使用有线耳机，避免回授啸叫

## 安装

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 运行

```bash
python realtime_voice_changer.py --mode pitch_down
```

可选参数：

```bash
python realtime_voice_changer.py --mode robot --samplerate 48000 --blocksize 1024 --gain 1.2
```

## 模式说明

- `pitch_up`：+4 半音
- `pitch_down`：-4 半音
- `robot`：环形调制 + 轻度失真

## 环境依赖怎么开放

如果你在公司网络、校园网或内网环境下安装依赖失败（例如 403 / proxy 错误），可以按下面方式开放：

1. **最推荐：配置 PyPI 镜像源**

```bash
pip config set global.index-url https://pypi.org/simple
# 或你们公司允许的镜像源
```

2. **如果必须走代理，配置代理环境变量**

```bash
set HTTP_PROXY=http://<proxy-host>:<port>
set HTTPS_PROXY=http://<proxy-host>:<port>
pip install -r requirements.txt
```

3. **无法联网时：离线安装（内网常用）**

在可联网机器上：

```bash
pip download -r requirements.txt -d wheels
```

把 `wheels/` 目录拷到目标机器后：

```bash
pip install --no-index --find-links=./wheels -r requirements.txt
```

4. **快速自检命令**

```bash
python realtime_voice_changer.py --help
python -c "import numpy, sounddevice, scipy; print('deps ok')"
```

## 重要提醒（合法合规）

- 未经授权，不要伪造、冒充或克隆他人声音。
- 涉及肖像权、声音权、平台条款或当地法律时，请先确认合规。
