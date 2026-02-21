import argparse
import queue
import sys
from dataclasses import dataclass


def _load_audio_deps():
    try:
        import numpy as np
        import sounddevice as sd
        from scipy.signal import resample
    except ModuleNotFoundError as exc:
        missing = getattr(exc, "name", "unknown")
        print(
            "缺少运行依赖: {}\n"
            "请先安装依赖：pip install -r requirements.txt\n"
            "如果网络受限，请查看 README 中的“环境依赖怎么开放”章节。".format(missing),
            file=sys.stderr,
        )
        raise SystemExit(2) from exc
    return np, sd, resample


@dataclass
class AudioConfig:
    samplerate: int = 44100
    channels: int = 1
    blocksize: int = 1024
    gain: float = 1.0


class VoiceProcessor:
    def __init__(self, mode: str, samplerate: int, np_module, resample_fn):
        self.mode = mode
        self.samplerate = samplerate
        self._phase = 0.0
        self.np = np_module
        self.resample = resample_fn

    def process(self, audio):
        if self.mode == "pitch_up":
            return self._pitch_shift(audio, semitones=4)
        if self.mode == "pitch_down":
            return self._pitch_shift(audio, semitones=-4)
        if self.mode == "robot":
            return self._robot(audio)
        return audio

    def _pitch_shift(self, audio, semitones: float):
        ratio = 2 ** (semitones / 12.0)
        shifted_len = max(1, int(len(audio) / ratio))
        shifted = self.resample(audio, shifted_len)
        restored = self.resample(shifted, len(audio))
        return restored.astype(self.np.float32)

    def _robot(self, audio):
        t = self.np.arange(len(audio), dtype=self.np.float32) / self.samplerate
        carrier_freq = 70.0
        carrier = self.np.sin(2 * self.np.pi * carrier_freq * t + self._phase)
        self._phase += 2 * self.np.pi * carrier_freq * len(audio) / self.samplerate
        modulated = audio * carrier
        clipped = self.np.tanh(2.0 * modulated)
        return clipped.astype(self.np.float32)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Windows 实时变声器")
    parser.add_argument(
        "--mode",
        choices=["pitch_up", "pitch_down", "robot", "clean"],
        default="pitch_down",
        help="变声模式",
    )
    parser.add_argument("--samplerate", type=int, default=44100)
    parser.add_argument("--blocksize", type=int, default=1024)
    parser.add_argument("--gain", type=float, default=1.0)
    return parser.parse_args()


def run() -> int:
    args = parse_args()
    np, sd, resample = _load_audio_deps()

    cfg = AudioConfig(
        samplerate=args.samplerate,
        blocksize=args.blocksize,
        gain=args.gain,
    )
    processor = VoiceProcessor(
        mode=args.mode,
        samplerate=cfg.samplerate,
        np_module=np,
        resample_fn=resample,
    )
    q: queue.Queue[str] = queue.Queue()

    def callback(indata, outdata, frames, time, status):
        if status:
            q.put(str(status))
        mono = indata[:, 0].astype(np.float32)
        processed = processor.process(mono) * cfg.gain
        processed = np.clip(processed, -1.0, 1.0)
        outdata[:] = processed.reshape(-1, 1)

    print("实时变声器已启动，按 Ctrl+C 退出")
    print(f"模式: {args.mode}, 采样率: {cfg.samplerate}, 块大小: {cfg.blocksize}")

    try:
        with sd.Stream(
            samplerate=cfg.samplerate,
            blocksize=cfg.blocksize,
            channels=cfg.channels,
            dtype="float32",
            callback=callback,
        ):
            while True:
                try:
                    message = q.get(timeout=0.2)
                    print(f"[Audio warning] {message}")
                except queue.Empty:
                    pass
    except KeyboardInterrupt:
        print("\n已停止")
        return 0
    except Exception as exc:
        print(f"运行失败: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(run())
