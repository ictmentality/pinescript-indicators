#!/usr/bin/env python3

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


SRT_TIME_RE = re.compile(
    r"(?P<sh>\d{2}):(?P<sm>\d{2}):(?P<ss>\d{2})[,.](?P<sms>\d{3})"
    r"\s+-->\s+"
    r"(?P<eh>\d{2}):(?P<em>\d{2}):(?P<es>\d{2})[,.](?P<ems>\d{3})"
)


def run_command(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def probe_duration(video_path):
    result = run_command(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(video_path),
        ]
    )
    return float(result.stdout.strip())


def format_timestamp(seconds):
    total_ms = int(round(seconds * 1000))
    hours = total_ms // 3_600_000
    total_ms %= 3_600_000
    minutes = total_ms // 60_000
    total_ms %= 60_000
    secs = total_ms // 1000
    ms = total_ms % 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{ms:03d}"


def normalize_text(text):
    return re.sub(r"\s+", " ", text).strip()


def word_count(text):
    return len(re.findall(r"\S+", text))


def parse_srt_timestamp(match, prefix):
    hours = int(match.group(f"{prefix}h"))
    minutes = int(match.group(f"{prefix}m"))
    seconds = int(match.group(f"{prefix}s"))
    millis = int(match.group(f"{prefix}ms"))
    return hours * 3600 + minutes * 60 + seconds + millis / 1000


def parse_srt_segments(srt_path):
    raw = srt_path.read_text(encoding="utf-8", errors="ignore").replace("\r\n", "\n")
    blocks = re.split(r"\n\s*\n", raw)
    segments = []
    for block in blocks:
        lines = [line.strip("\ufeff") for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        time_line = None
        text_lines = []
        for idx, line in enumerate(lines):
            if SRT_TIME_RE.fullmatch(line):
                time_line = line
                text_lines = lines[idx + 1 :]
                break
        if not time_line or not text_lines:
            continue
        match = SRT_TIME_RE.fullmatch(time_line)
        start_seconds = parse_srt_timestamp(match, "s")
        end_seconds = parse_srt_timestamp(match, "e")
        text = normalize_text(" ".join(text_lines))
        if not text:
            continue
        segments.append(
            {
                "start_seconds": start_seconds,
                "end_seconds": end_seconds,
                "text": text,
                "words": word_count(text),
            }
        )
    return segments


def parse_transcript_segments(transcript_path, duration_seconds):
    raw = transcript_path.read_text(encoding="utf-8", errors="ignore").replace("\r\n", "\n")
    lines = [normalize_text(line) for line in raw.splitlines()]
    lines = [line for line in lines if line]
    if not lines:
        return []

    weights = [max(word_count(line), 1) for line in lines]
    total_weight = sum(weights)
    segments = []
    elapsed = 0.0

    for line, weight in zip(lines, weights):
        segment_duration = duration_seconds * (weight / total_weight)
        segments.append(
            {
                "start_seconds": elapsed,
                "end_seconds": elapsed + segment_duration,
                "text": line,
                "words": weight,
            }
        )
        elapsed += segment_duration

    if segments:
        segments[-1]["end_seconds"] = duration_seconds
    return segments


def build_chunks(segments, chunk_seconds, max_words):
    chunks = []
    current = []
    current_words = 0

    for segment in segments:
        if not current:
            current = [segment]
            current_words = segment["words"]
            continue

        current_duration = segment["end_seconds"] - current[0]["start_seconds"]
        next_words = current_words + segment["words"]
        if current_duration > chunk_seconds or next_words > max_words:
            chunks.append(finalize_chunk(len(chunks), current))
            current = [segment]
            current_words = segment["words"]
            continue

        current.append(segment)
        current_words = next_words

    if current:
        chunks.append(finalize_chunk(len(chunks), current))

    return chunks


def finalize_chunk(index, segments):
    start_seconds = segments[0]["start_seconds"]
    end_seconds = segments[-1]["end_seconds"]
    transcript_text = "\n".join(segment["text"] for segment in segments)
    compact_text = normalize_text(transcript_text.replace("\n", " "))
    words = word_count(compact_text)
    return {
        "index": index,
        "start_seconds": start_seconds,
        "end_seconds": end_seconds,
        "start_timestamp": format_timestamp(start_seconds),
        "end_timestamp": format_timestamp(end_seconds),
        "duration_seconds": round(end_seconds - start_seconds, 3),
        "word_count": words,
        "segment_count": len(segments),
        "transcript_text": transcript_text,
        "transcript_compact": compact_text,
    }


def frame_timestamps(start_seconds, end_seconds, frames_per_chunk):
    if frames_per_chunk <= 0:
        return []
    span = max(end_seconds - start_seconds, 0.01)
    if frames_per_chunk == 1:
        return [start_seconds + span / 2]

    times = []
    for idx in range(frames_per_chunk):
        ratio = (idx + 1) / (frames_per_chunk + 1)
        times.append(start_seconds + span * ratio)
    return times


def extract_frame(video_path, output_path, timestamp_seconds):
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-ss",
            f"{timestamp_seconds:.3f}",
            "-i",
            str(video_path),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(output_path),
        ],
        check=True,
    )


def ocr_image(image_path):
    if shutil.which("tesseract") is None:
        return ""
    result = subprocess.run(
        ["tesseract", str(image_path), "stdout", "--psm", "6"],
        check=True,
        capture_output=True,
        text=True,
    )
    return normalize_text(result.stdout)


def default_transcript_path(video_path):
    transcripts_dir = video_path.parent / "transcripts"
    candidate = transcripts_dir / f"{video_path.stem} transcript.txt"
    return candidate if candidate.exists() else None


def default_srt_paths(video_path):
    home_bundle_dir = Path.home() / "Desktop" / "futures-made-simple"
    transcripts_dir = video_path.parent / "transcripts"
    return [
        video_path.with_suffix(".srt"),
        video_path.parent / f"{video_path.stem}.srt",
        video_path.parent / f"{video_path.stem}_srt.srt",
        transcripts_dir / f"{video_path.stem}.srt",
        transcripts_dir / f"{video_path.stem}_srt.srt",
        home_bundle_dir / f"{video_path.stem}.srt",
        home_bundle_dir / f"{video_path.stem}_srt.srt",
    ]


def resolve_srt_path(video_path, explicit_srt):
    if explicit_srt:
        return explicit_srt if explicit_srt.exists() else None
    for candidate in default_srt_paths(video_path):
        if candidate.exists():
            return candidate
    return None


def resolve_transcript_path(video_path, explicit_transcript):
    if explicit_transcript:
        return explicit_transcript if explicit_transcript.exists() else None
    return default_transcript_path(video_path)


def ensure_tools():
    missing = [tool for tool in ("ffmpeg", "ffprobe") if shutil.which(tool) is None]
    if missing:
        raise RuntimeError(f"Missing required tool(s): {', '.join(missing)}")


def build_bundle_for_video(
    video_path,
    transcript_path,
    srt_path,
    output_root,
    chunk_seconds,
    max_words,
    frames_per_chunk,
    run_ocr,
):
    duration_seconds = probe_duration(video_path)
    alignment_mode = None

    if srt_path and srt_path.exists():
        segments = parse_srt_segments(srt_path)
        alignment_mode = "subtitle_timestamps"
    elif transcript_path and transcript_path.exists():
        segments = parse_transcript_segments(transcript_path, duration_seconds)
        alignment_mode = "estimated_from_plain_transcript"
    else:
        raise RuntimeError(
            f"No transcript or SRT found for {video_path.name}. "
            "Provide --transcript or --srt, or place matching files in the expected locations."
        )

    if not segments:
        raise RuntimeError(f"No usable transcript segments found for {video_path.name}")

    output_dir = output_root / video_path.stem
    frames_dir = output_dir / "frames"
    output_dir.mkdir(parents=True, exist_ok=True)
    frames_dir.mkdir(parents=True, exist_ok=True)

    chunks = build_chunks(segments, chunk_seconds=chunk_seconds, max_words=max_words)

    for chunk in chunks:
        chunk_frames = []
        for frame_index, timestamp_seconds in enumerate(
            frame_timestamps(
                chunk["start_seconds"],
                chunk["end_seconds"],
                frames_per_chunk=frames_per_chunk,
            ),
            start=1,
        ):
            frame_name = f"chunk_{chunk['index']:03d}_frame_{frame_index:02d}.jpg"
            frame_path = frames_dir / frame_name
            extract_frame(video_path, frame_path, timestamp_seconds)
            ocr_text = ocr_image(frame_path) if run_ocr else ""
            chunk_frames.append(
                {
                    "timestamp_seconds": round(timestamp_seconds, 3),
                    "timestamp": format_timestamp(timestamp_seconds),
                    "file": str(frame_path.relative_to(output_dir)),
                    "ocr_text": ocr_text,
                }
            )
        chunk["frames"] = chunk_frames

    transcript_source = srt_path if srt_path and srt_path.exists() else transcript_path
    bundle = {
        "bundle_version": 1,
        "video": {
            "file": str(video_path),
            "stem": video_path.stem,
            "duration_seconds": round(duration_seconds, 3),
            "duration_timestamp": format_timestamp(duration_seconds),
        },
        "transcript": {
            "file": str(transcript_source) if transcript_source else None,
            "alignment_mode": alignment_mode,
            "notes": (
                "Chunk timestamps come from subtitle timing."
                if alignment_mode == "subtitle_timestamps"
                else "Chunk timestamps are estimated from transcript word distribution because no SRT timing was found."
            ),
        },
        "settings": {
            "chunk_seconds": chunk_seconds,
            "max_words": max_words,
            "frames_per_chunk": frames_per_chunk,
            "ocr_enabled": run_ocr,
        },
        "summarization_prompt_hint": (
            "Summarize the video chunk by chunk using transcript_text as the primary source. "
            "Use frame OCR and the frame timestamps to recover slide titles, chart labels, and on-screen cues. "
            "Call out concepts, examples, action items, and any important terminology."
        ),
        "chunks": chunks,
    }

    bundle_path = output_dir / "bundle.json"
    bundle_path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return bundle_path, len(chunks)


def iter_videos(input_path):
    if input_path.is_file():
        return [input_path]
    return sorted(path for path in input_path.glob("*.mp4") if path.is_file())


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Build a JSON bundle for GPT video summarization by chunking transcript text, "
            "extracting representative frames, and OCR'ing those frames."
        )
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to a single .mp4 file or a directory of .mp4 files.",
    )
    parser.add_argument(
        "--transcript",
        type=Path,
        help="Optional path to a plain-text transcript for single-video mode.",
    )
    parser.add_argument(
        "--srt",
        type=Path,
        help="Optional path to an SRT file for single-video mode.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("helpers/video_summary_bundles"),
        help="Directory where bundles and extracted frames will be written.",
    )
    parser.add_argument(
        "--chunk-seconds",
        type=int,
        default=180,
        help="Target chunk duration in seconds.",
    )
    parser.add_argument(
        "--max-words",
        type=int,
        default=900,
        help="Maximum approximate words per chunk before splitting.",
    )
    parser.add_argument(
        "--frames-per-chunk",
        type=int,
        default=2,
        help="How many representative frames to extract per chunk.",
    )
    parser.add_argument(
        "--skip-ocr",
        action="store_true",
        help="Skip OCR even if tesseract is available.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    ensure_tools()

    input_path = args.input.resolve()
    output_root = args.output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    videos = iter_videos(input_path)
    if not videos:
        raise RuntimeError(f"No .mp4 files found at {input_path}")

    single_video_mode = len(videos) == 1 and input_path.is_file()
    results = []
    for video_path in videos:
        transcript_path = resolve_transcript_path(video_path, args.transcript if single_video_mode else None)
        srt_path = resolve_srt_path(video_path, args.srt if single_video_mode else None)
        bundle_path, chunk_count = build_bundle_for_video(
            video_path=video_path,
            transcript_path=transcript_path,
            srt_path=srt_path,
            output_root=output_root,
            chunk_seconds=args.chunk_seconds,
            max_words=args.max_words,
            frames_per_chunk=args.frames_per_chunk,
            run_ocr=not args.skip_ocr,
        )
        results.append((video_path, bundle_path, chunk_count))

    for video_path, bundle_path, chunk_count in results:
        print(f"{video_path.name}: {chunk_count} chunks -> {bundle_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
