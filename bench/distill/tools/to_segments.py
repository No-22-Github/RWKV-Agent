#!/usr/bin/env python3
"""Convert packed rows (text + loss_spans) to rwkv_state_tune masked rows.

  to_segments.py --rows <dataset/train/rows.jsonl> --out <segments.jsonl>

rwkv_lightning_cuda 47df608 trains on {"segments":[{"text","train"}]} rows:
each segment is tokenized on its own and only train=true tokens are loss
targets. Its reader accepts exactly one field per row, so meta is dropped.

Two details the conversion must get right:
- loss_spans are code-point offsets (Python str indices), not byte offsets.
- Every span starts right after "Assistant: ". The space is moved into the
  trained segment, so the untrained prefix ends with "Assistant:" exactly as
  the inference prompt does (inference.AppendAssistantOpening), and the model
  learns its own first token (" <", " 57", ...). Cutting after the space
  instead splits World tokens like " <" and changes tokenization in 2073 of
  2157 v1.3 train rows; with the space moved, segment-wise and whole-text
  tokenization are identical on every row.
"""
import argparse
import json

OPENING = "Assistant:"


def segments(text, spans):
    out = []
    at = 0
    for start, end in spans:
        if not (at <= start < end <= len(text)):
            raise ValueError("loss spans must be ordered, non-empty and inside the text")
        if text[start - 1] == " " and text[: start - 1].endswith(OPENING):
            start -= 1
        else:
            raise ValueError("loss span does not start after %r" % (OPENING + " "))
        if start > at:
            out.append({"text": text[at:start], "train": False})
        out.append({"text": text[start:end], "train": True})
        at = end
    if at < len(text):
        out.append({"text": text[at:], "train": False})
    if "".join(s["text"] for s in out) != text:
        raise ValueError("segments do not reassemble the text")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    rows = trained = total = 0
    with open(args.out, "w") as out:
        for line in open(args.rows):
            row = json.loads(line)
            segs = segments(row["text"], row["loss_spans"])
            out.write(json.dumps({"segments": segs}, ensure_ascii=False) + "\n")
            rows += 1
            total += len(row["text"])
            trained += sum(len(s["text"]) for s in segs if s["train"])
    print("%d rows, trained chars %d / %d (%.1f%%)" % (rows, trained, total, 100 * trained / total))


if __name__ == "__main__":
    main()
